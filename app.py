"""
Pool Attendance App - Versione Web con Streamlit
"""

import streamlit as st
import json
import os
import hashlib
import calendar
from datetime import datetime, date
from typing import Optional, List, Dict
import base64

# ─── Configurazione pagina ───────────────────────────────────────────────────
st.set_page_config(
    page_title="🏊 Pool Attendance App",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Costanti ────────────────────────────────────────────────────────────────
DATA_DIR = "data"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SCORING_RULES_FILE = os.path.join(DATA_DIR, "scoring_rules.json")
SCORE_ENTRIES_FILE = os.path.join(DATA_DIR, "score_entries.json")
PHOTO_DIR = os.path.join(DATA_DIR, "team_photos")

DEFAULT_SCORING_RULES = [
    {"rule_id": "presenza",             "name": "Presenza",             "points": 1, "description": "Presenza alla sessione"},
    {"rule_id": "portare_birre",        "name": "Portare Birre",        "points": 3, "description": "Porta da bere per tutti"},
    {"rule_id": "organizzazione_evento","name": "Organizzazione Evento","points": 5, "description": "Organizza un evento"},
    {"rule_id": "pulizia_area",         "name": "Pulizia Area",         "points": 2, "description": "Pulisce l'area"},
    {"rule_id": "aiuto_setup",          "name": "Aiuto Setup",          "points": 2, "description": "Aiuta nel setup"},
]

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
.stApp { background-color: #F0F8FF; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Header titolo ── */
.main-title {
    background: linear-gradient(135deg, #0077BE, #00A8E8);
    color: white;
    padding: 14px 18px;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 14px;
    box-shadow: 0 4px 15px rgba(0,119,190,0.3);
}
.main-title h1 { margin: 0; font-size: 1.5em; }
.main-title p  { margin: 3px 0 0; opacity: 0.85; font-size: 0.88em; }

/* ── Pill punteggio ── */
.rule-pill {
    display: inline-block;
    background: #E3F2FD;
    color: #0077BE;
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 0.9em;
}

/* ── Sidebar (desktop) ── */
[data-testid="stSidebar"] { background: #0077BE !important; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 10px !important;
    width: 100% !important;
    margin: 3px 0 !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.3) !important;
}

/* ── Bottoni generali ── */
.stButton > button { border-radius: 10px; font-weight: 600; transition: all 0.2s; }

/* ══ DESKTOP ══ */
@media (min-width: 769px) {
    .block-container { padding-top: 1rem; }
    #mobile-bottom-nav { display: none !important; }
}

/* ══ MOBILE ══ */
@media (max-width: 768px) {
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 85px !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }
    /* Nascondi sidebar e il suo toggle su mobile: usiamo la bottom nav */
    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebarUserContent"] { display: none !important; }
}

/* ══ BOTTOM NAVIGATION BAR (solo mobile) ══ */
#mobile-bottom-nav { display: none; }

@media (max-width: 768px) {
    #mobile-bottom-nav {
        display: flex !important;
        position: fixed;
        bottom: 0; left: 0; right: 0;
        z-index: 99999;
        background: linear-gradient(135deg, #005f9e, #0077BE);
        box-shadow: 0 -3px 20px rgba(0,0,0,0.35);
        border-top: 1px solid rgba(255,255,255,0.18);
        padding: 0; gap: 0;
    }
    #mobile-bottom-nav > div[data-testid="stHorizontalBlock"] {
        width: 100% !important; gap: 0 !important; padding: 0 !important;
    }
    #mobile-bottom-nav > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        padding: 0 !important; flex: 1 !important;
    }
    /* Wrapper bottone nav */
    .bnav-wrap { width: 100%; }
    .bnav-wrap button {
        background: transparent !important;
        color: rgba(255,255,255,0.6) !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 5px 1px 9px !important;
        font-size: 9.5px !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em !important;
        white-space: pre-line !important;
        line-height: 1.5 !important;
        min-height: 62px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
        -webkit-tap-highlight-color: transparent !important;
        transition: background 0.15s, color 0.15s !important;
    }
    .bnav-wrap button:hover,
    .bnav-wrap button:focus {
        background: rgba(255,255,255,0.12) !important;
        border: none !important; box-shadow: none !important;
    }
    /* Voce attiva: sfondo pill dorato */
    .bnav-active button {
        color: #FFD700 !important;
        background: rgba(255,215,0,0.12) !important;
        border-top: 3px solid #FFD700 !important;
        padding-top: 2px !important;
    }

    /* ── Calendario mobile: celle più visibili ── */
    .cal-day-btn button {
        border-radius: 10px !important;
        font-size: 12px !important;
        padding: 4px 2px !important;
        min-height: 44px !important;
    }
    .cal-today button {
        background: #0077BE !important;
        color: white !important;
        font-weight: 900 !important;
        border: 2px solid #005f9e !important;
    }
    .cal-has-events button {
        background: #E3F2FD !important;
        color: #0055A5 !important;
        border: 2px solid #90CAF9 !important;
        font-weight: 700 !important;
    }
    .cal-selected button {
        background: #FF6B35 !important;
        color: white !important;
        border: 2px solid #D45A28 !important;
        font-weight: 900 !important;
    }

    /* ── Admin: testi più leggibili ── */
    .admin-card {
        background: white;
        border-radius: 12px;
        padding: 14px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #0077BE;
    }
}

/* ── Admin cards (anche desktop) ── */
.admin-card {
    background: white;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 8px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-left: 4px solid #0077BE;
    color: #1a1a2e;
}
.admin-stat-box {
    background: linear-gradient(135deg, #0077BE, #00A8E8);
    color: white !important;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    font-size: 1.1em;
    font-weight: 700;
    margin: 4px 0;
    box-shadow: 0 3px 10px rgba(0,119,190,0.3);
}
.admin-stat-box .val { font-size: 2em; display: block; margin-bottom: 4px; }
.rule-row {
    display: flex;
    align-items: center;
    background: white;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 6px 0;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border-left: 4px solid #27AE60;
    gap: 12px;
    color: #1a1a2e;
}
.rule-row .rname { font-weight: 700; font-size: 1em; color: #1a1a2e; flex: 1; }
.rule-row .rpts  { background: #0077BE; color: white; border-radius: 20px; padding: 3px 12px; font-weight: 700; font-size: 0.9em; }
.log-row {
    background: #F8FBFF;
    border-radius: 8px;
    padding: 8px 12px;
    margin: 4px 0;
    border-left: 3px solid #90CAF9;
    font-size: 0.88em;
    color: #1a1a2e;
}
.log-date { color: #0077BE; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# GESTIONE DATI
# ═══════════════════════════════════════════════════════════════════

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PHOTO_DIR, exist_ok=True)

def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

def load_users() -> Dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return {u["username"]: u for u in json.load(f)}
    return {}

def save_users(users: Dict):
    ensure_dirs()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(users.values()), f, indent=2, ensure_ascii=False)

def init_admin():
    users = load_users()
    if "admin" not in users:
        users["admin"] = {
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "is_admin": True,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        save_users(users)

def load_teams() -> Dict:
    if os.path.exists(TEAMS_FILE):
        with open(TEAMS_FILE, 'r', encoding='utf-8') as f:
            return {t["team_id"]: t for t in json.load(f)}
    return {}

def save_teams(teams: Dict):
    ensure_dirs()
    with open(TEAMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(teams.values()), f, indent=2, ensure_ascii=False)

def load_scoring_rules() -> Dict:
    if os.path.exists(SCORING_RULES_FILE):
        with open(SCORING_RULES_FILE, 'r', encoding='utf-8') as f:
            return {r["rule_id"]: r for r in json.load(f)}
    return {}

def save_scoring_rules(rules: Dict):
    ensure_dirs()
    with open(SCORING_RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(rules.values()), f, indent=2, ensure_ascii=False)

def init_scoring_rules():
    rules = load_scoring_rules()
    if not rules:
        for r in DEFAULT_SCORING_RULES:
            r = dict(r)
            r["created_at"] = datetime.now().isoformat()
            r["is_active"] = True
            rules[r["rule_id"]] = r
        save_scoring_rules(rules)

def load_score_entries() -> List:
    if os.path.exists(SCORE_ENTRIES_FILE):
        with open(SCORE_ENTRIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_score_entries(entries: List):
    ensure_dirs()
    with open(SCORE_ENTRIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def add_score_entry(team_id: str, rule_id: str, date_str: str, notes: str = "") -> bool:
    teams = load_teams()
    rules = load_scoring_rules()
    if team_id not in teams or rule_id not in rules:
        return False
    points = rules[rule_id]["points"]
    entries = load_score_entries()
    entries.append({
        "team_id": team_id, "rule_id": rule_id, "date": date_str,
        "points": points, "notes": notes,
        "created_at": datetime.now().isoformat()
    })
    save_score_entries(entries)
    teams[team_id]["total_score"] = teams[team_id].get("total_score", 0) + points
    save_teams(teams)
    return True

def get_entries_for_date(date_str: str) -> List:
    return [e for e in load_score_entries() if e["date"] == date_str]

def get_entries_for_month(year: int, month: int) -> List:
    prefix = f"{year}-{month:02d}"
    return [e for e in load_score_entries() if e["date"].startswith(prefix)]

def save_team_photo(team_id: str, uploaded_file) -> Optional[str]:
    ensure_dirs()
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    path = os.path.join(PHOTO_DIR, f"{team_id}{ext}")
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def get_team_photo_b64(photo_path: str) -> Optional[str]:
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as f:
            data = f.read()
        ext  = os.path.splitext(photo_path)[1].lower().strip(".")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif"}.get(ext, "png")
        return f"data:image/{mime};base64,{base64.b64encode(data).decode()}"
    return None


# ═══════════════════════════════════════════════════════════════════
# AUTENTICAZIONE
# ═══════════════════════════════════════════════════════════════════

def login(username: str, password: str) -> bool:
    users = load_users()
    user  = users.get(username)
    if user and user["password_hash"] == hash_password(password):
        users[username]["last_login"] = datetime.now().isoformat()
        save_users(users)
        st.session_state.logged_in   = True
        st.session_state.username    = username
        st.session_state.is_admin    = user["is_admin"]
        return True
    return False

def logout():
    st.session_state.logged_in    = False
    st.session_state.username     = None
    st.session_state.is_admin     = False
    st.session_state.current_page = "classifica"


# ═══════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════

def init_session():
    defaults = {
        "logged_in":    False,
        "username":     None,
        "is_admin":     False,
        "current_page": "classifica",
        "cal_year":     datetime.now().year,
        "cal_month":    datetime.now().month,
        "selected_date":None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════
# NAVIGAZIONE
# ═══════════════════════════════════════════════════════════════════

def render_bottom_nav():
    """
    Bottom nav bar per mobile: bottoni Streamlit reali stilizzati via CSS
    in modo da sembrare una barra fissa in basso. Niente JS custom.
    """
    page     = st.session_state.current_page
    is_admin = st.session_state.is_admin

    items = [
        ("classifica", "🏆", "Classifica"),
        ("calendario", "📅", "Calendario"),
        ("squadre",    "👥", "Squadre"),
    ]
    if is_admin:
        items.append(("admin", "⚙️", "Admin"))
    items.append(("_logout", "🚪", "Esci"))

    # Contenitore fisso in basso (visibile solo su mobile via CSS già definito)
    st.markdown('<div id="mobile-bottom-nav">', unsafe_allow_html=True)
    cols = st.columns(len(items))
    for i, (key, icon, label) in enumerate(items):
        active_style = "bnav-active" if page == key else ""
        with cols[i]:
            # Il bottone usa una classe CSS custom per lo stile
            st.markdown(
                f'<div class="bnav-wrap {active_style}" data-nav="{key}">',
                unsafe_allow_html=True
            )
            if st.button(f"{icon}\n{label}", key=f"bnav_{key}", use_container_width=True):
                if key == "_logout":
                    logout()
                else:
                    st.session_state.current_page = key
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🏊 Pool App")
        st.markdown(f"👤 **{st.session_state.username}**")
        if st.session_state.is_admin:
            st.markdown("👑 _Amministratore_")
        st.markdown("---")

        pages = [
            ("🏆 Classifica", "classifica"),
            ("📅 Calendario", "calendario"),
            ("👥 Squadre",    "squadre"),
        ]
        if st.session_state.is_admin:
            pages.append(("⚙️ Admin", "admin"))

        for label, page_key in pages:
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# PAGINE
# ═══════════════════════════════════════════════════════════════════

def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="main-title">
            <h1>🏊 Pool Attendance App</h1>
            <p>Gestione Presenze & Punteggi Piscina</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🔐 Accedi")
        with st.form("login_form"):
            username  = st.text_input("👤 Username", placeholder="Inserisci username")
            password  = st.text_input("🔑 Password", type="password", placeholder="Inserisci password")
            submitted = st.form_submit_button("Accedi", use_container_width=True, type="primary")
            if submitted:
                if login(username, password):
                    st.rerun()
                else:
                    st.error("❌ Username o password non corretti")
        st.markdown("---")
        st.caption("💡 Prima volta? Usa **admin / admin123** poi cambia la password nel pannello Admin.")


# ── Classifica ──────────────────────────────────────────────────────
def page_classifica():
    st.markdown("""
    <div class="main-title">
        <h1>🏆 Classifica Squadre</h1>
        <p>Punteggi aggiornati in tempo reale</p>
    </div>
    """, unsafe_allow_html=True)

    teams = load_teams()
    if not teams:
        st.info("🏊 Nessuna squadra ancora. Vai su **Squadre** per crearne una!")
        return

    sorted_teams  = sorted(teams.values(), key=lambda t: t.get("total_score", 0), reverse=True)
    medals        = {0: "🥇", 1: "🥈", 2: "🥉"}
    border_colors = {0: "#FFD700", 1: "#C0C0C0", 2: "#CD7F32"}
    max_score     = max((t.get("total_score", 0) for t in sorted_teams), default=1) or 1

    for i, team in enumerate(sorted_teams):
        medal       = medals.get(i, f"#{i+1}")
        score       = team.get("total_score", 0)
        border      = border_colors.get(i, "#0077BE")
        members_str = ", ".join(m["name"] for m in team.get("members", [])) or "Nessun membro"

        col_photo, col_info, col_score = st.columns([1, 5, 2])
        with col_photo:
            photo_b64 = get_team_photo_b64(team.get("photo_path"))
            if photo_b64:
                st.markdown(
                    f'<img src="{photo_b64}" style="width:52px;height:52px;border-radius:50%;'
                    f'object-fit:cover;border:3px solid {border};">',
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<div style='font-size:2.2em;text-align:center;'>🏊</div>", unsafe_allow_html=True)
        with col_info:
            st.markdown(f"### {medal} {team['name']}")
            st.caption(f"👥 {members_str}")
        with col_score:
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#0077BE,#00A8E8);color:white;"
                f"border-radius:50px;padding:9px 14px;text-align:center;"
                f"font-size:1.2em;font-weight:bold;margin-top:8px;'>⭐ {score} pt</div>",
                unsafe_allow_html=True
            )
        st.progress(score / max_score)
        st.markdown("---")


# ── Calendario ──────────────────────────────────────────────────────
def page_calendario():
    st.markdown("""
    <div class="main-title">
        <h1>📅 Calendario Presenze</h1>
        <p>Tocca un giorno per registrare presenze</p>
    </div>
    """, unsafe_allow_html=True)

    today = date.today()

    # Auto-seleziona oggi al primo accesso
    if st.session_state.selected_date is None:
        st.session_state.selected_date = today.strftime("%Y-%m-%d")

    # Navigazione mese
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("◀", use_container_width=True):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12; st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with col2:
        month_names = ["","Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno",
                       "Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]
        st.markdown(
            f"<h2 style='text-align:center;color:#0077BE;margin:0;font-size:1.2em;'>"
            f"📅 {month_names[st.session_state.cal_month]} {st.session_state.cal_year}</h2>",
            unsafe_allow_html=True
        )
    with col3:
        if st.button("▶", use_container_width=True):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1; st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    # Bottone "Vai ad oggi"
    if (st.session_state.cal_month != today.month or st.session_state.cal_year != today.year):
        if st.button("📍 Vai ad oggi", use_container_width=True, type="primary"):
            st.session_state.cal_month = today.month
            st.session_state.cal_year  = today.year
            st.session_state.selected_date = today.strftime("%Y-%m-%d")
            st.rerun()

    month_entries    = get_entries_for_month(st.session_state.cal_year, st.session_state.cal_month)
    days_with_events = set(e["date"] for e in month_entries)

    # Intestazioni giorni
    day_names = ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"]
    cols = st.columns(7)
    for i, d in enumerate(day_names):
        with cols[i]:
            color = "#E74C3C" if i >= 5 else "#0077BE"
            st.markdown(
                f"<div style='text-align:center;font-weight:800;color:{color};"
                f"padding:6px 0;font-size:0.82em;letter-spacing:0.04em;'>{d}</div>",
                unsafe_allow_html=True
            )

    # Griglia giorni con stile CSS per ogni stato
    for week in calendar.monthcalendar(st.session_state.cal_year, st.session_state.cal_month):
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("<div style='min-height:44px;'></div>", unsafe_allow_html=True)
                else:
                    date_str   = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                    is_today   = (date_str == today.strftime("%Y-%m-%d"))
                    has_events = date_str in days_with_events
                    is_selected= (date_str == st.session_state.selected_date)
                    is_weekend = (i >= 5)

                    # Scegli classe CSS per stile bottone
                    if is_selected:
                        css_class = "cal-selected"
                        label = f"**{day}**" + ("\n✅" if has_events else "")
                    elif is_today:
                        css_class = "cal-today"
                        label = f"**{day}**\n📍"
                    elif has_events:
                        css_class = "cal-has-events"
                        label = f"{day}\n🔵"
                    else:
                        css_class = "cal-day-btn"
                        label = str(day)

                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                    if st.button(label, key=f"day_{date_str}", use_container_width=True):
                        st.session_state.selected_date = date_str
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # Legenda visiva
    st.markdown("""
    <div style='display:flex;gap:12px;flex-wrap:wrap;margin:10px 0 4px;font-size:0.8em;color:#555;'>
        <span>📍 Oggi</span>
        <span>🔵 Ha attività</span>
        <span style='background:#FF6B35;color:white;border-radius:6px;padding:1px 7px;'>Selezionato</span>
    </div>
    """, unsafe_allow_html=True)

    # Pannello giorno selezionato
    st.markdown("---")
    sel_date    = st.session_state.selected_date
    day_entries = get_entries_for_date(sel_date)
    teams       = load_teams()
    rules       = load_scoring_rules()

    # Formatta data in italiano
    try:
        sel_dt = datetime.strptime(sel_date, "%Y-%m-%d")
        giorno_ita = ["lunedì","martedì","mercoledì","giovedì","venerdì","sabato","domenica"][sel_dt.weekday()]
        month_names2 = ["","gennaio","febbraio","marzo","aprile","maggio","giugno",
                        "luglio","agosto","settembre","ottobre","novembre","dicembre"]
        data_bella = f"{giorno_ita.capitalize()} {sel_dt.day} {month_names2[sel_dt.month]} {sel_dt.year}"
    except:
        data_bella = sel_date

    oggi_label = " 📍 (oggi)" if sel_date == today.strftime("%Y-%m-%d") else ""
    st.markdown(
        f"<div style='background:white;border-radius:12px;padding:12px 16px;"
        f"border-left:4px solid #0077BE;box-shadow:0 2px 8px rgba(0,0,0,0.07);margin-bottom:10px;'>"
        f"<span style='font-size:1.1em;font-weight:700;color:#0077BE;'>📌 {data_bella}{oggi_label}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    if day_entries:
        st.markdown("**Attività registrate:**")
        for entry in day_entries:
            tn = teams.get(entry["team_id"], {}).get("name", entry["team_id"])
            rn = rules.get(entry["rule_id"], {}).get("name", entry["rule_id"])
            st.markdown(
                f'<div style="background:#E8F5E9;border-radius:8px;padding:8px 12px;margin:4px 0;">'
                f'🏊 <b>{tn}</b> · {rn} · <span style="color:#27AE60;font-weight:700;">+{entry["points"]} pt</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown("")

    if st.session_state.is_admin and teams and rules:
        with st.expander("➕ Assegna Punteggio", expanded=not bool(day_entries)):
            with st.form(f"score_form_{sel_date}"):
                team_options = {t["name"]: tid for tid, t in teams.items()}
                rule_options = {r["name"]: rid for rid, r in rules.items() if r.get("is_active", True)}
                sel_team = st.selectbox("🏊 Squadra", list(team_options.keys()))
                sel_rule = st.selectbox("⭐ Tipo attività", list(rule_options.keys()))
                notes    = st.text_input("📝 Note (opzionale)")
                if sel_rule:
                    pts = rules[rule_options[sel_rule]]["points"]
                    st.markdown(
                        f'<div style="background:#E3F2FD;border-radius:8px;padding:8px 12px;color:#0055A5;font-weight:700;">'
                        f'⭐ Punti assegnati: +{pts}</div>',
                        unsafe_allow_html=True
                    )
                if st.form_submit_button("✅ Assegna Punteggio", type="primary", use_container_width=True):
                    if add_score_entry(team_options[sel_team], rule_options[sel_rule], sel_date, notes):
                        st.success("✅ Punteggio assegnato!")
                        st.rerun()
    elif not st.session_state.is_admin:
        st.markdown(
            '<div style="background:#FFF3E0;border-radius:8px;padding:8px 12px;color:#E65100;font-size:0.9em;">' +
            '🔒 Solo gli admin possono assegnare punteggi.</div>',
            unsafe_allow_html=True
        )


# ── Squadre ─────────────────────────────────────────────────────────
def page_squadre():
    st.markdown("""
    <div class="main-title">
        <h1>👥 Gestione Squadre</h1>
        <p>Crea e gestisci le squadre</p>
    </div>
    """, unsafe_allow_html=True)

    teams = load_teams()

    if st.session_state.is_admin:
        with st.expander("➕ Crea Nuova Squadra", expanded=not bool(teams)):
            with st.form("new_team_form"):
                col1, col2 = st.columns(2)
                with col1: team_id   = st.text_input("ID Squadra", placeholder="team_rossi")
                with col2: team_name = st.text_input("Nome Squadra", placeholder="I Rossi")
                photo = st.file_uploader("📷 Foto squadra (opzionale)", type=["jpg","jpeg","png"])
                if st.form_submit_button("✅ Crea Squadra", type="primary", use_container_width=True):
                    if not team_id or not team_name:
                        st.error("❌ Compila ID e Nome squadra.")
                    elif team_id in teams:
                        st.error("❌ ID già esistente.")
                    else:
                        photo_path = save_team_photo(team_id, photo) if photo else None
                        teams[team_id] = {
                            "team_id": team_id, "name": team_name,
                            "photo_path": photo_path, "members": [],
                            "total_score": 0,
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat()
                        }
                        save_teams(teams)
                        st.success(f"✅ Squadra **{team_name}** creata!")
                        st.rerun()

    if not teams:
        st.info("🏊 Nessuna squadra ancora.")
        return

    for team_id, team in teams.items():
        with st.expander(f"🏊 {team['name']} — ⭐ {team.get('total_score', 0)} pt"):
            col1, col2 = st.columns([1, 3])
            with col1:
                photo_b64 = get_team_photo_b64(team.get("photo_path"))
                if photo_b64:
                    st.markdown(
                        f'<img src="{photo_b64}" style="width:110px;height:110px;'
                        f'border-radius:12px;object-fit:cover;">',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div style="width:110px;height:110px;background:#E3F2FD;'
                        'border-radius:12px;display:flex;align-items:center;'
                        'justify-content:center;font-size:2.5em;">🏊</div>',
                        unsafe_allow_html=True
                    )
                if st.session_state.is_admin:
                    new_photo = st.file_uploader("Cambia foto", type=["jpg","jpeg","png"], key=f"photo_{team_id}")
                    if new_photo:
                        fresh = load_teams()
                        fresh[team_id]["photo_path"] = save_team_photo(team_id, new_photo)
                        save_teams(fresh)
                        st.rerun()

            with col2:
                st.markdown(f"**ID:** `{team_id}`")
                members = team.get("members", [])
                st.markdown(f"**Membri ({len(members)}):**")

                if members:
                    for m in members:
                        col_m, col_btn = st.columns([4, 1])
                        with col_m:
                            st.markdown(f"• **{m['name']}** _{m.get('role','membro')}_")
                        with col_btn:
                            if st.session_state.is_admin:
                                if st.button("🗑", key=f"del_m_{team_id}_{m['name']}"):
                                    fresh = load_teams()
                                    fresh[team_id]["members"] = [
                                        x for x in fresh[team_id]["members"] if x["name"] != m["name"]
                                    ]
                                    save_teams(fresh)
                                    st.rerun()
                else:
                    st.caption("Nessun membro ancora")

                if st.session_state.is_admin:
                    with st.form(f"add_member_{team_id}"):
                        st.markdown("**➕ Aggiungi membro**")
                        new_member = st.text_input("Nome membro", placeholder="Es. Mario Rossi")
                        new_role   = st.selectbox("Ruolo", ["membro", "capitano", "vice"])
                        if st.form_submit_button("Aggiungi", type="primary", use_container_width=True):
                            if new_member.strip():
                                # Ricarica sempre da file → evita sovrascritture
                                fresh       = load_teams()
                                cur_members = fresh.get(team_id, {}).get("members", [])
                                if any(m["name"].lower() == new_member.strip().lower() for m in cur_members):
                                    st.error("❌ Membro già presente.")
                                else:
                                    cur_members.append({
                                        "name":      new_member.strip(),
                                        "role":      new_role,
                                        "joined_at": datetime.now().isoformat()
                                    })
                                    fresh[team_id]["members"]    = cur_members
                                    fresh[team_id]["updated_at"] = datetime.now().isoformat()
                                    save_teams(fresh)
                                    st.success(f"✅ {new_member.strip()} aggiunto!")
                                    st.rerun()
                            else:
                                st.error("❌ Inserisci un nome valido.")

            if st.session_state.is_admin:
                st.markdown("---")
                if st.button(f"🗑️ Elimina squadra {team['name']}", key=f"del_team_{team_id}"):
                    fresh = load_teams()
                    del fresh[team_id]
                    save_teams(fresh)
                    st.rerun()


# ── Admin ────────────────────────────────────────────────────────────
def page_admin():
    st.markdown("""
    <div class="main-title">
        <h1>⚙️ Pannello Admin</h1>
        <p>Gestione regole, statistiche e utenti</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⭐ Regole Punteggio", "📊 Statistiche", "👤 Utenti"])

    # ── Tab Regole ────────────────────────────────────────────────────
    with tab1:
        rules = load_scoring_rules()
        st.markdown("### Regole attive")

        for rule_id, rule in rules.items():
            stato = "🟢 Attiva" if rule.get("is_active", True) else "🔴 Disattiva"
            bg    = "white" if rule.get("is_active", True) else "#FFF5F5"
            st.markdown(
                f'<div class="rule-row" style="background:{bg};">' +
                f'<span class="rname">⭐ {rule["name"]}</span>' +
                f'<span class="rpts">{rule["points"]} pt</span>' +
                f'<span style="font-size:0.8em;color:#555;">{stato}</span>' +
                '</div>',
                unsafe_allow_html=True
            )
            c1, c2 = st.columns([1, 1])
            with c1:
                active = st.checkbox(
                    "Attiva" if not rule.get("is_active", True) else "Disattiva",
                    value=rule.get("is_active", True),
                    key=f"active_{rule_id}"
                )
                if active != rule.get("is_active", True):
                    rules[rule_id]["is_active"] = active
                    save_scoring_rules(rules)
                    st.rerun()
            with c2:
                if st.button(f"🗑️ Elimina", key=f"del_rule_{rule_id}"):
                    del rules[rule_id]; save_scoring_rules(rules); st.rerun()

        st.markdown("---")
        st.markdown(
            '<div style="background:#E8F5E9;border-radius:10px;padding:14px 16px;margin-bottom:10px;">' +
            '<b style="color:#1B5E20;">➕ Aggiungi Nuova Regola</b></div>',
            unsafe_allow_html=True
        )
        with st.form("new_rule_form"):
            r_name = st.text_input("📝 Nome regola", placeholder="Es. Pulizia spogliatoi")
            c1, c2 = st.columns(2)
            with c1: r_pts  = st.number_input("⭐ Punti", min_value=1, max_value=100, value=1)
            with c2: r_desc = st.text_input("📋 Descrizione", placeholder="Opzionale")
            if st.form_submit_button("✅ Aggiungi Regola", type="primary", use_container_width=True):
                if r_name:
                    r_id = r_name.lower().replace(" ", "_")
                    if r_id in rules:
                        st.error("❌ Regola già esistente")
                    else:
                        rules[r_id] = {"rule_id": r_id, "name": r_name, "points": r_pts,
                                       "description": r_desc,
                                       "created_at": datetime.now().isoformat(), "is_active": True}
                        save_scoring_rules(rules)
                        st.success(f"✅ Regola '{r_name}' aggiunta!")
                        st.rerun()

    # ── Tab Statistiche ───────────────────────────────────────────────
    with tab2:
        teams   = load_teams()
        entries = load_score_entries()
        rules   = load_scoring_rules()

        # Box statistiche colorate
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="admin-stat-box"><span class="val">🏊 {len(teams)}</span>Squadre</div>',
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f'<div class="admin-stat-box"><span class="val">📅 {len(entries)}</span>Attività</div>',
                unsafe_allow_html=True
            )
        with c3:
            tot = sum(e["points"] for e in entries)
            st.markdown(
                f'<div class="admin-stat-box"><span class="val">⭐ {tot}</span>Punti totali</div>',
                unsafe_allow_html=True
            )

        if entries and teams:
            st.markdown("---")
            st.markdown("### 📊 Punteggi per squadra")
            max_s = max((t.get("total_score", 0) for t in teams.values()), default=1) or 1
            for t in sorted(teams.values(), key=lambda x: x.get("total_score", 0), reverse=True):
                score = t.get("total_score", 0)
                st.markdown(
                    f'<div class="admin-card">' +
                    f'<b style="color:#0077BE;">{t["name"]}</b> ' +
                    f'<span style="float:right;background:#0077BE;color:white;border-radius:20px;' +
                    f'padding:2px 12px;font-size:0.85em;font-weight:700;">⭐ {score} pt</span></div>',
                    unsafe_allow_html=True
                )
                st.progress(score / max_s)

            st.markdown("---")
            st.markdown("### 📋 Ultimi 20 movimenti")
            for e in sorted(entries, key=lambda x: x["created_at"], reverse=True)[:20]:
                tn = teams.get(e["team_id"], {}).get("name", e["team_id"])
                rn = rules.get(e["rule_id"], {}).get("name", e["rule_id"])
                st.markdown(
                    f'<div class="log-row">' +
                    f'<span class="log-date">{e["date"]}</span> · ' +
                    f'<b>{tn}</b> · {rn} · ' +
                    f'<span style="color:#27AE60;font-weight:700;">+{e["points"]} pt</span>' +
                    '</div>',
                    unsafe_allow_html=True
                )

    # ── Tab Utenti ────────────────────────────────────────────────────
    with tab3:
        users = load_users()
        st.markdown("### 👤 Utenti registrati")
        for uname, user in users.items():
            badge = '👑 Admin' if user["is_admin"] else '👤 Utente'
            bg    = "#FFF9E6" if user["is_admin"] else "white"
            st.markdown(
                f'<div class="admin-card" style="background:{bg};">' +
                f'<b style="font-size:1em;color:#1a1a2e;">{uname}</b> ' +
                f'<span style="background:#E3F2FD;color:#0055A5;border-radius:12px;padding:2px 10px;font-size:0.8em;">{badge}</span> ' +
                f'<span style="color:#888;font-size:0.8em;float:right;">dal {user["created_at"][:10]}</span></div>',
                unsafe_allow_html=True
            )
            if uname != "admin":
                if st.button(f"🗑️ Rimuovi {uname}", key=f"del_user_{uname}"):
                    del users[uname]; save_users(users); st.rerun()

        st.markdown("---")
        st.markdown(
            '<div style="background:#E8F5E9;border-radius:10px;padding:12px 16px;margin-bottom:8px;">' +
            '<b style="color:#1B5E20;">➕ Nuovo Utente</b></div>',
            unsafe_allow_html=True
        )
        with st.form("new_user_form"):
            n_user  = st.text_input("👤 Username")
            n_pwd   = st.text_input("🔑 Password", type="password")
            n_admin = st.checkbox("👑 Ruolo Admin")
            if st.form_submit_button("✅ Crea Utente", type="primary", use_container_width=True):
                if n_user and n_pwd:
                    if n_user in users:
                        st.error("❌ Username già esistente")
                    else:
                        users[n_user] = {
                            "username": n_user,
                            "password_hash": hash_password(n_pwd),
                            "is_admin": n_admin,
                            "created_at": datetime.now().isoformat(),
                            "last_login": None
                        }
                        save_users(users)
                        st.success(f"✅ Utente '{n_user}' creato!")
                        st.rerun()

        st.markdown("---")
        st.markdown(
            '<div style="background:#E3F2FD;border-radius:10px;padding:12px 16px;margin-bottom:8px;">' +
            '<b style="color:#0055A5;">🔑 Cambia la tua password</b></div>',
            unsafe_allow_html=True
        )
        with st.form("change_pwd_form"):
            old_pwd = st.text_input("Password attuale", type="password")
            new_pwd = st.text_input("Nuova password",   type="password")
            if st.form_submit_button("🔑 Aggiorna Password", type="primary", use_container_width=True):
                cur = users.get(st.session_state.username)
                if cur and cur["password_hash"] == hash_password(old_pwd):
                    users[st.session_state.username]["password_hash"] = hash_password(new_pwd)
                    save_users(users)
                    st.success("✅ Password aggiornata con successo!")
                else:
                    st.error("❌ Password attuale errata")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    ensure_dirs()
    init_admin()
    init_scoring_rules()
    init_session()

    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()       # visibile solo su desktop via CSS
    render_bottom_nav()    # visibile solo su mobile via CSS

    page = st.session_state.current_page
    if page == "classifica":
        page_classifica()
    elif page == "calendario":
        page_calendario()
    elif page == "squadre":
        page_squadre()
    elif page == "admin":
        if st.session_state.is_admin:
            page_admin()
        else:
            st.error("❌ Accesso negato")


if __name__ == "__main__":
    main()
