import streamlit as st

# --- Konfiguracja aplikacji ---
st.set_page_config(
    page_title="Prosty Magazyn Towarów",
    layout="centered"
)
st.title("📦 Prosty Magazyn Towarów")
st.markdown("---")

# --- Inicjalizacja Magazynu (Lista Towarów w Stanie Sesji) ---
# Używamy st.session_state, aby lista była zachowana pomiędzy interakcjami.
if 'towary' not in st.session_state:
    st.session_state['towary'] = [] # Pusta lista do przechowywania nazw towarów

# --- Funkcje Obsługi Magazynu ---

def dodaj_towar(nazwa):
    """Dodaje nowy towar do listy."""
    # Używamy .upper() dla prostego formatowania i unikania duplikatów 
    # różniących się tylko wielkością liter.
    towar_sformatowany = nazwa.strip().upper()
    if towar_sformatowany and towar_sformatowany not in st.session_state.towary:
        st.session_state.towary.append(towar_sformatowany)
        st.success(f"Dodano towar: **{towar_sformatowany}**")
    elif not towar_sformatowany:
        st.error("Wpisz nazwę towaru.")
    else:
        st.warning(f"Towar **{towar_sformatowany}** już jest w magazynie.")

def usun_towar(nazwa):
    """Usuwa towar z listy."""
    towar_sformatowany = nazwa.strip().upper()
    try:
        st.session_state.towary.remove(towar_sformatowany)
        st.info(f"Usunięto towar: **{towar_sformatowany}**")
    except ValueError:
        st.error(f"Błąd: Towar **{towar_sformatowany}** nie został znaleziony w magazynie.")


# --- Sekcja Dodawania Towaru ---
st.header("➕ Dodaj Nowy Towar")
with st.form(key='dodaj_form'):
    nowy_towar = st.text_input("Nazwa Towaru", key='input_dodaj')
    submit_button_dodaj = st.form_submit_button(label='Dodaj do Magazynu')

if submit_button_dodaj:
    dodaj_towar(nowy_towar)


# --- Sekcja Wyświetlania Magazynu ---
st.header("📋 Stan Magazynu")
if st.session_state.towary:
    # Sortujemy listę alfabetycznie dla lepszej prezentacji
    st.session_state.towary.sort() 
    
    # Wyświetlenie listy za pomocą indeksów
    lista_wyswietlana = [f"{i+1}. {towar}" for i, towar in enumerate(st.session_state.towary)]
    st.markdown("\n".join(lista_wyswietlana))
    
    # Można też użyć st.dataframe lub st.table, ale markdown jest prostszy
    # st.table(st.session_state.towary) 
else:
    st.write("Magazyn jest **pusty**.")


# --- Sekcja Usuwania Towaru ---
st.header("➖ Usuń Towar")
if st.session_state.towary:
    # Wybór towaru z listy rozwijanej
    towar_do_usuniecia = st.selectbox(
        "Wybierz towar do usunięcia",
        st.session_state.towary,
        key='select_usun'
    )
    
    if st.button("Usuń z Magazynu", key='button_usun'):
        usun_towar(towar_do_usuniecia)
else:
    st.info("Brak towarów do usunięcia.")


st.markdown("---")
st.caption("Aplikacja działa w oparciu o pamięć sesji Streamlit.")
