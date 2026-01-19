import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- Konfiguracja połączenia Supabase ---
# Dane znajdziesz w Supabase -> Settings -> API
SUPABASE_URL = "TWOJ_URL_SUPABASE"
SUPABASE_KEY = "TWOJ_ANON_KEY"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- Konfiguracja aplikacji ---
st.set_page_config(page_title="Magazyn Supabase", layout="centered")
st.title("📦 Magazyn Towarów (Baza Supabase)")
st.markdown("---")

# --- Funkcje Obsługi Bazy Danych ---

def pobierz_dane():
    """Pobiera wszystkie produkty z tabeli."""
    response = supabase.table("magazyn").select("*").order("nazwa").execute()
    return response.data

def sformatuj_nazwe(nazwa):
    return nazwa.strip().upper()

def dodaj_lub_aktualizuj(nazwa, ilosc):
    nazwa_key = sformatuj_nazwe(nazwa)
    if not nazwa_key or ilosc <= 0:
        st.error("Niepoprawne dane.")
        return

    # Sprawdzamy czy towar istnieje
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa_key).execute()
    
    if existing.data:
        nowa_suma = existing.data[0]['ilosc'] + ilosc
        supabase.table("magazyn").update({"ilosc": nowa_suma}).eq("nazwa", nazwa_key).execute()
        st.success(f"Zaktualizowano {nazwa_key}. Stan: {nowa_suma}")
    else:
        supabase.table("magazyn").insert({"nazwa": nazwa_key, "ilosc": ilosc}).execute()
        st.success(f"Dodano nowy towar: {nazwa_key}")

def zmien_stan(nazwa, zmiana, operacja):
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa).execute()
    if not existing.data:
        return

    obecna_ilosc = existing.data[0]['ilosc']
    if operacja == "Wydanie (Odejmij)":
        if obecna_ilosc < zmiana:
            st.error("Brak wystarczającej ilości!")
            return
        nowa_ilosc = obecna_ilosc - zmiana
    else:
        nowa_ilosc = obecna_ilosc + zmiana

    if nowa_ilosc == 0:
        supabase.table("magazyn").delete().eq("nazwa", nazwa).execute()
        st.warning(f"Produkt {nazwa} wyczerpany i usunięty.")
    else:
        supabase.table("magazyn").update({"ilosc": nowa_ilosc}).eq("nazwa", nazwa).execute()
        st.success(f"Nowy stan {nazwa}: {nowa_ilosc}")

def usun_calkowicie(nazwa):
    supabase.table("magazyn").delete().eq("nazwa", nazwa).execute()
    st.info(f"Usunięto {nazwa} z bazy.")

# --- INTERFEJS UŻYTKOWNIKA ---

# 1. Dodawanie
st.header("➕ Dodaj / Uzupełnij")
with st.form("dodaj_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    nowa_nazwa = col1.text_input("Nazwa Towaru")
    nowa_ilosc = col2.number_input("Ilość", min_value=1, step=1)
    if st.form_submit_button("Wyślij do Bazy"):
        dodaj_lub_aktualizuj(nowa_nazwa, nowa_ilosc)

# 2. Wyświetlanie
st.header("📋 Aktualny Stan (z Supabase)")
dane_z_bazy = pobierz_dane()
if dane_z_bazy:
    df = pd.DataFrame(dane_z_bazy)
    # Wyświetlamy tylko nazwę i ilość
    st.dataframe(df[["nazwa", "ilosc"]], use_container_width=True, hide_index=True)
else:
    st.info("Baza jest pusta.")

# 3. Modyfikacja i Usuwanie
if dane_z_bazy:
    st.header("🔄 Operacje")
    lista_nazw = [item['nazwa'] for item in dane_z_bazy]
    
    with st.expander("Zmień ilość lub usuń produkt"):
        wybrany = st.selectbox("Wybierz produkt", lista_nazw)
        
        c1, c2, c3 = st.columns([2,1,1])
        op = c1.radio("Operacja", ["Przyjęcie (Dodaj)", "Wydanie (Odejmij)"])
        ile = c2.number_input("Ile", min_value=1, step=1)
        
        if st.button("Wykonaj zmianę"):
            zmien_stan(wybrany, ile, op)
            st.rerun()
            
        st.divider()
        if st.button("🔥 USUŃ PRODUKT Z BAZY"):
            usun_calkowicie(wybrany)
            st.rerun()

st.markdown("---")
st.caption("Dane są przechowywane w chmurze Supabase i nie znikną po odświeżeniu strony.")
