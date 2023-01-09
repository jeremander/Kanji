from collections import defaultdict
import json
import random
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd
import streamlit as st

JSONDict = Dict[str, Any]

st.set_page_config(page_title = 'Kanji Flashcards', page_icon = '🇯🇵', layout = 'centered')

KANJIDIC_PATH = 'kanjidic/kanjidic.json'

@st.experimental_memo
def load_kanjidic():
    with open(KANJIDIC_PATH) as f:
        d = json.load(f)
    for (i, entry) in enumerate(d['entries']):
        entry['_id'] = i
    return d

@st.experimental_memo
def get_entries(filters: JSONDict):
    kanjidic = load_kanjidic()
    entries = kanjidic['entries']
    # apply filters to entries
    valid_entries = []
    for entry in entries:
        for (filter_name, d) in kanjidic['filters'].items():
            if (filter_name in filters):
                filter_field = d['field']
                if (filter_field in entry):
                    val = entry[filter_field]
                    filter_vals = filters[filter_name]
                    if (val in filter_vals):
                        if (not filter_vals[val]):
                            break
                    else:
                        if (not filter_vals.get(None, False)):
                            break
        else:  # entry is valid
            valid_entries.append(entry)
    return valid_entries

def make_sidebar() -> JSONDict:
    kanjidic = load_kanjidic()
    modes = kanjidic['modes']
    filters = kanjidic.get('filters', {})
    with st.sidebar:
        st.caption('Choose flashcard front & back')
        chosen_mode = st.selectbox('Mode', list(modes), index = 0)
        chosen_filters = defaultdict(dict)
        for (filter_name, d) in filters.items():
            st.caption(filter_name)
            for val in d['values']:
                if (val is None):
                    label = 'Other'
                else:
                    label = str(val)
                chosen_filters[filter_name][val] = st.checkbox(label, True)
    st.session_state['options'] = {'mode' : chosen_mode, 'filters' : chosen_filters}

def get_valid_entries() -> List[JSONDict]:
    filters = st.session_state['options']['filters']
    return get_entries(filters)

def get_random_index() -> Optional[int]:
    entries = get_valid_entries()
    num_entries = len(entries)
    if (num_entries == 0):
        return None
    random_entry = random.choice(entries)
    return random_entry['_id']

def random_card() -> None:
    st.session_state['entry_index'] = get_random_index()

def make_info_group(group: str, entry: JSONDict, front: bool) -> None:
    group_data = load_kanjidic()['groups'][group]
    info = group_data['info']
    extra = group_data.get('extra', {})
    (col1, col2) = st.columns(2)
    for (field, field_name) in info.items():
        val = entry[field]
        if (not val):
            val = '[N/A]'
        if front:
            col1.caption(field_name)
            col1.header(val)
        else:
            col1.markdown(f'__{field_name}__: &nbsp; {val}', unsafe_allow_html = True)
    d = {}
    for (field, field_name) in extra.items():
        val = entry[field]
        if (val is None):
            val = '—'
        d[field_name] = val
    if d:
        df = pd.Series(d).to_frame()
        styler = df.style
        styler.hide(axis = 'columns')
        styler.set_table_styles([
            {'selector' : 'tr', 'props' : 'line-height: 14px;'}
        ])
        col2.write(styler.to_html() + '<br>', unsafe_allow_html = True)

def make_card_face(groups: Sequence[str], entry: JSONDict, front: bool) -> None:
    for group in groups:
        make_info_group(group, entry, front)

def main():
    kanjidic = load_kanjidic()
    entries = kanjidic['entries']
    st.title('Kanji Flashcards')
    make_sidebar()
    valid_entries = get_valid_entries()
    num_valid_entries = len(valid_entries)
    st.caption(f'({num_valid_entries:,d} cards)')
    options = st.session_state['options']
    if ('entry_index' not in st.session_state):
        random_card()
    st.button('Next card', on_click = random_card)
    entry_index = st.session_state['entry_index']
    if (entry_index is not None):
        entry = entries[entry_index]
        mode = options['mode']
        faces = kanjidic['modes'][mode]
        with st.expander('Front', expanded = True):
            make_card_face(faces['front'], entry, True)
        with st.expander('Back', expanded = False):
            make_card_face(faces['back'], entry, False)

main()