# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd


class TablePicker:

    @st.cache_data(show_spinner=False)
    def get_databases(_self):
        inventory = _self.session.sql("show tables in account").collect()
        ret_inv = pd.DataFrame(inventory)[["database_name", "schema_name", "name"]]
        return ret_inv

    def __init__(self):
        self.session = get_active_session()
        self.tables = self.get_databases()

        self.object_css = """
        <style>
        
        div[class*="st-key-menu_item_"] > div[class="stButton"]{
         max-height:.70rem;
         padding:0px;
        }
        div[class*="st-key-menu_item_"] button{
            appearance:none;
            justify-content:flex-start;
            max-height:.45rem;
            min-height:1.5rem;
            color:#7f7f7f;
            padding-left:.5rem;
            margin:0px;
            border:none;
            background-color:white;
        }
        div[class*="st-key-menu_item_"] button:hover{
        background-color:#f1f1f1;
        color:#7f7f7f;
        }
        div[class*="st-key-menu_item_"] button:active{
        background-color:#f1f1f1;
        color:#7f7f7f;
        }
        div[class*="st-key-menu_item_"] button p{
            font-size:12px;
            margin:0px;
            padding:0px;
            text-overflow: ellipsis;
            white-space: nowrap;
            overflow: hidden;
        }
        div[class*="st-key-menu_item_"] button p:hover{
            overflow: visible;
        }
        .st-key-menu_container{
            background-color:white;
            max-height:900px;
            overflow-y:scroll;
            overflow-x:hidden;
            padding-top:1rem;
            padding-bottom:1rem;
        }
        div[class*="st-key-menu_item_schema_"] button{
        margin-left:2rem;
        }
        div[class*="st-key-menu_item_table_"] button{
        margin-left:4rem;
        }
        
        </style>
        """
        st.html(self.object_css)

        if "scoped_db" not in st.session_state:
            st.session_state["scoped_db"] = None
        if "scoped_schema" not in st.session_state:
            st.session_state["scoped_schema"] = None
        if "scoped_table" not in st.session_state:
            st.session_state["scoped_table"] = None

    @staticmethod
    def set_database_scope(key: str) -> None:
        if st.session_state["scoped_db"] == key:
            st.session_state["scoped_db"] = None
            st.session_state["scoped_schema"] = None
            st.session_state["scoped_table"] = None
        else:
            st.session_state["scoped_db"] = key
            st.session_state["scoped_schema"] = None
            st.session_state["scoped_table"] = None

    @staticmethod
    def set_schema_scope(key: str) -> None:
        if st.session_state["scoped_schema"] == key:
            st.session_state["scoped_schema"] = None
            st.session_state["scoped_table"] = None
        else:
            st.session_state["scoped_schema"] = key
            st.session_state["scoped_table"] = None

    @staticmethod
    def set_table_scope(key: str) -> None:
        if st.session_state["scoped_table"] == key:
            st.session_state["scoped_table"] = None
        else:
            st.session_state["scoped_table"] = key

    @staticmethod
    def render_button(
        level: str, label: str, primary: bool, key: str, on_click: callable, args: list
    ):
        levels = {
            "db": ":material/database:",
            "schema": ":material/schema:",
            "table": ":material/table:",
        }
        if level == "table":
            icon = {}
        else:
            icon = {
                "icon": (
                    ":material/keyboard_arrow_down:"
                    if primary
                    else ":material/chevron_right:"
                )
            }
        st.button(
            f"{levels.get(level)}$~~${label}",
            key=f"menu_item_{level}_{key}",
            use_container_width=True,
            on_click=on_click,
            args=args,
            **icon,
        )

    def menu(self):
        with st.container(key="menu_container"):
            for database in sorted(self.tables["database_name"].unique()):
                self.render_button(
                    level="db",
                    label=database,
                    primary=(
                        True if st.session_state["scoped_db"] == database else False
                    ),
                    key=database,
                    on_click=self.set_database_scope,
                    args=[database],
                )

                if st.session_state["scoped_db"] == database:
                    for schemas in sorted(
                        self.tables.loc[self.tables["database_name"] == database][
                            "schema_name"
                        ].unique()
                    ):
                        self.render_button(
                            level="schema",
                            label=schemas,
                            primary=(
                                True
                                if st.session_state["scoped_db"] == database
                                and st.session_state["scoped_schema"] == schemas
                                else False
                            ),
                            key=schemas,
                            on_click=self.set_schema_scope,
                            args=[schemas],
                        )
                        if (
                            st.session_state["scoped_db"] == database
                            and st.session_state["scoped_schema"] == schemas
                        ):
                            for table in sorted(
                                self.tables.loc[
                                    (self.tables["database_name"] == database)
                                    & (self.tables["schema_name"] == schemas)
                                ]["name"].unique()
                            ):

                                self.render_button(
                                    level="table",
                                    label=table,
                                    primary=(
                                        True
                                        if st.session_state["scoped_db"] == database
                                        and st.session_state["scoped_schema"] == schemas
                                        and st.session_state["scoped_table"] == table
                                        else False
                                    ),
                                    key=table,
                                    on_click=self.set_table_scope,
                                    args=[table],
                                )

    def get_path(self):
        path = [
            st.session_state["scoped_db"],
            st.session_state["scoped_schema"],
            st.session_state["scoped_table"],
        ]
        if all(path):
            table = ".".join(path)
            return table
