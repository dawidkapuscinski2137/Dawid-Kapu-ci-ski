import streamlit as st
import pandas as pd

# --- Konfiguracja aplikacji ---
st.set_page_config(
    page_title="Magazyn Towarów z Ilością",
    layout="centered"
)
st.title("📦 Magazyn Towarów z Ilością")
st.markdown("---")

# --- Inicjalizacja Magazynu (Słownik w Stanie Sesji) ---
# Magazyn jest słownikiem: {NAZWA_TOWARU: ILOŚĆ}
# Używamy st.session_state, aby dane były zachowane pomiędzy interakcjami.
if 'magazyn' not in st.session_state:
    st.session_state['magazyn'] = {} 

# --- Funkcje Pomocnicze ---

def sformatuj_nazwe(nazwa):
    """Formatuje nazwę towaru do ujednoliconego klucza słownika."""
    # Używamy .upper() i .strip() dla spójności kluczy
    return nazwa.strip().upper()

# --- Funkcje Obsługi Magazynu ---

def dodaj_nowy_towar(nazwa, ilosc):
    """Dodaje nowy towar do magazynu lub zwiększa jego ilość, jeśli już istnieje."""
    towar_key = sformatuj_nazwe(nazwa)
    
    if not towar_key or ilosc <= 0:
        st.error("Wpisz poprawną nazwę towaru i ilość (większą niż 0).")
        return

    if towar_key not in st.session_state.magazyn:
        st.session_state.magazyn[towar_key] = ilosc
        st.success(f"Dodano nowy towar: **{towar_key}** w ilości: **{ilosc}**.")
    else:
        st.session_state.magazyn[towar_key] += ilosc
        st.success(f"Zwiększono stan towaru **{towar_key}** o **{ilosc}**. Nowy stan: **{st.session_state.magazyn[towar_key]}**.")

def modyfikuj_ilosc(nazwa, zmiana_ilosci, operacja):
    """Zmienia ilość danego towaru (dodaje lub odejmuje)."""
    towar_key = sformatuj_nazwe(nazwa)
    
    if not towar_key or zmiana_ilosci <= 0:
        st.error("Wybierz towar i podaj poprawną ilość (większą niż 0).")
        return

    if towar_key not in st.session_state.magazyn:
        st.warning(f"Towar **{towar_key}** nie istnieje w magazynie.")
        return

    obecna_ilosc = st.session_state.magazyn[towar_key]
    
    if operacja == "Przyjęcie (Dodaj)":
        st.session_state.magazyn[towar_key] += zmiana_ilosci
        st.success(f"Przyjęto **{zmiana_ilosci}** do **{towar_key}**. Nowy stan: **{st.session_state.magazyn[towar_key]}**.")
    
    elif operacja == "Wydanie (Odejmij)":
        if obecna_ilosc >= zmiana_ilosci:
            st.session_state.magazyn[towar_key] -= zmiana_ilosci
            st.info(f"Wydano **{zmiana_ilosci}** z **{towar_key}**. Nowy stan: **{st.session_state.magazyn[towar_key]}**.")
            
            # Usuwamy towar, jeśli ilość spadnie do zera
            if st.session_state.magazyn[towar_key] == 0:
                del st.session_state.magazyn[towar_key]
                st.warning(f"Towar **{towar_key}** osiągnął stan 0 i został usunięty z listy magazynowej.")
        else:
            st.error(f"Nie można wydać {zmiana_ilosci}. W magazynie jest tylko {obecna_ilosc} sztuk **{towar_key}**.")

def usun_towar_calkowicie(nazwa):
    """Usuwa towar całkowicie z magazynu (cały klucz ze słownika)."""
    towar_key = sformatuj_nazwe(nazwa)
    
    if towar_key in st.session_state.magazyn:
        del st.session_state.magazyn[towar_key]
        st.info(f"Towar **{towar_key}** został **CAŁKOWICIE** usunięty z magazynu.")
    else:
        st.warning(f"Błąd: Towar **{towar_key}** nie został znaleziony.")


# --- 1. Sekcja Dodawania Nowego Towaru / Uzupełniania Ilości ---
st.header("➕ Dodaj Nowy Towar / Uzupełnij Ilość")
with st.form(key='dodaj_form'):
    col1, col2 = st.columns(2)
    with col1:
        nowy_towar = st.text_input("Nazwa Towaru", key='input_dodaj')
    with col2:
        ilosc_do_dodania = st.number_input("Ilość do dodania", min_value=1, value=1, step=1, key='input_ilosc_dodaj')
    
    submit_button_dodaj = st.form_submit_button(label='Dodaj/Uzupełnij Magazyn')

if submit_button_dodaj:
    dodaj_nowy_towar(nowy_towar, ilosc_do_dodania)


# --- 2. Sekcja Wyświetlania Magazynu ---
st.header("📋 Stan Magazynu")
if st.session_state.magazyn:
    # Tworzenie DataFrame z Pandas dla ładniejszego wyświetlania tabelarycznego
    df = pd.DataFrame(st.session_state.magazyn.items(), columns=["Nazwa Towaru", "Ilość"])
    
    # Sortowanie alfabetyczne po nazwie towaru
    df = df.sort_values(by="Nazwa Towaru").reset_index(drop=True)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.write(f"**Łączna liczba różnych towarów:** {len(st.session_state.magazyn)}")
else:
    st.info("Magazyn jest **pusty**.")


# --- 3. Sekcja Modyfikacji Ilości (Przyjęcie/Wydanie) ---
st.header("🔄 Zmień Ilość Towaru (Przyjęcie/Wydanie)")
if st.session_state.magazyn:
    # Lista kluczy do wyboru, posortowana alfabetycznie
    towary_do_wyboru = sorted(st.session_state.magazyn.keys())

    with st.form(key='modyfikuj_form'):
        col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
        
        with col_m1:
            towar_do_modyfikacji = st.selectbox(
                "Wybierz Towar",
                towary_do_wyboru,
                key='select_modyfikuj'
            )
        with col_m2:
            operacja = st.radio(
                "Operacja",
                ("Przyjęcie (Dodaj)", "Wydanie (Odejmij)"),
                key='radio_operacja'
            )
        with col_m3:
            ilosc_zmiany = st.number_input(
                "Ilość",
                min_value=1,
                value=1,
                step=1,
                key='input_ilosc_zmiany'
            )
            
        submit_button_modyfikuj = st.form_submit_button(label='Wykonaj Zmianę')

    if submit_button_modyfikuj:
        modyfikuj_ilosc(towar_do_modyfikacji, ilosc_zmiany, operacja)
else:
    st.info("Brak towarów do modyfikacji. Dodaj najpierw jakiś towar.")


# --- 4. Sekcja Całkowitego Usuwania Towaru ---
st.header("🔥 Całkowite Usunięcie Towaru")
if st.session_state.magazyn:
    towary_do_usuniecia = sorted(st.session_state.magazyn.keys())
    
    towar_do_usuniecia = st.selectbox(
        "Wybierz towar do CAŁKOWITEGO usunięcia",
        towary_do_usuniecia,
        key='select_usun_calkowicie'
    )
    
    # Przycisk bezpieczeństwa
    if st.button("USUŃ CAŁKOWICIE Z MAGAZYNU", key='button_usun_calkowicie'):
        usun_towar_calkowicie(towar_do_usuniecia)
else:
    st.info("Brak towarów do usunięcia.")


st.markdown("---")
st.caption("Aplikacja działa w oparciu o pamięć sesji Streamlit (dane znikną po zamknięciu zakładki).")
