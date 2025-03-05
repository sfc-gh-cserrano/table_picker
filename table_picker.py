# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
from string import Template
import numpy as np


class TablePicker:

    @st.cache_data(show_spinner=False)
    def get_databases(_self):
        inventory = _self.session.sql("show terse tables in account").collect()
        ret_inv = pd.DataFrame(inventory)[["database_name", "schema_name", "name"]]
        return ret_inv

    def __init__(self, height: int = -1):
        self.session = get_active_session()
        self.tables = self.get_databases()
        db_count = len(self.tables["database_name"].unique())
        self.height = (db_count * 30) + 60 if height == -1 else height + 60
        self.object_css = Template(
            """
        <style>
        
        div[class*="st-key-menu_item_"] > div[class="stButton"]{
         max-height:.8rem;
         padding:0px;
         margin:0px;
        }
        div[class*="st-key-menu_item_"] button{
            justify-content:flex-start;
            color:#7f7f7f;
            padding:1rem;
            padding-left:.5rem;
            border:none;
            border-radius:0px;
            width:100%;
            overflow-hidden;
            background-color:white;
            margin:0px;
            max-height:.75rem;
            min-height:.75rem;
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
        div[class*="st-key-menu_item_"] button:focus:not(:active){
            background-color:white;
            color:#7f7f7f;
        }

        
        div[height="$height"]:has(.st-key-menu_container){
            background-color:white;
            overflow-y:scroll;
            overflow-x:hidden;
            margin-bottom:1rem;
        }

        .st-key-menu_container div[data-testid="stPopover"] button{
        max-height:1.5rem;
        min-height:1.5rem;
        color:#7f7f7f;
        }
        .st-key-menu_container div[data-testid="stPopover"] button svg{
        height:1rem;
        color:#7f7f7f;
        }
        div[class*="st-key-menu_item_schema_"] button{
        margin-left:2rem;
        width:calc(100% - 2rem);
        }
        div[class*="st-key-menu_item_table_"] button{
        margin-left:4rem;
        width:calc(100% - 4rem);
        }
        .st-key-menu_search input{
        font-size:14px;
        color:#7f7f7f;
        height:1.75rem;
        }
        .st-key-menu_search div[data-testid="stTextInputRootElement"]{
        height:1.75rem;
        border:0px;
        }

        </style>
        """
        )
        st.html(self.object_css.substitute(height=self.height))

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
            use_container_width=False,
            on_click=on_click,
            args=args,
            **icon,
        )

    def filter_menu(self, text: str, columns: list):
        filter_mask = np.column_stack(
            [
                self.tables[col].astype(str).str.contains(text, na=False, case=False)
                for col in self.tables
                if col in columns
            ]
        )
        return self.tables.loc[filter_mask.any(axis=1)]

    def menu(self):
        with st.container(key="menu_container", border=True, height=self.height):
            search_menu = st.columns((2, 1))
            with search_menu[1].popover(
                "", icon=":material/settings:", use_container_width=True
            ):
                options = []
                if st.toggle("Database", value=True):
                    options.append("database_name")
                if st.toggle("Schema", value=True):
                    options.append("schema_name")
                if st.toggle("Table", value=True):
                    options.append("name")
            search_text = search_menu[0].text_input(
                "",
                key="menu_search",
                label_visibility="collapsed",
                placeholder="Search",
            )
            if search_text:
                inventory = self.filter_menu(text=search_text, columns=options)
            else:
                inventory = self.tables
            for database in sorted(inventory["database_name"].unique()):
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
                        inventory.loc[self.tables["database_name"] == database][
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
                                inventory.loc[
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
