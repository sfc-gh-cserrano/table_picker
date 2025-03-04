# SiS Table Picker

>Requires Streamlit 1.39 or greater

## Instructions

- Copy `table_picker.py` to your SiS app
- Import into your code

## Implement

```python
from table_picker import TablePicker

with st.sidebar:
    tb = TablePicker()
    tb.menu()
    table = tb.get_path()
```