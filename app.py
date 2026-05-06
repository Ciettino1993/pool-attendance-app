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
from io import BytesIO

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
    {"rule_id": "presenza", "name": "Presenza", "points": 1, "description": "Presenza alla sessione"},
    {"rule_id": "portare_birre", "name": "Portare Birre", "points": 3, "description": "Porta da bere per tutti"},
    {"rule_id": "organizzazione_evento", "name": "Organizzazione Evento", "points": 5, "description": "Organizza un evento"},
    {"rule_id": "pulizia_area", "name": "Pulizia Area", "points": 2, "description": "Pulisce l'area"},
    {"rule_id": "aiuto_setup", "name": "Aiuto Setup", "points": 2, "description": "Aiuta nel setup"},
]

COLORS = {
    "primary": "#0077BE",
    "secondary": "#FFD700",
    "accent": "#FF6B35",
    "background": "#F0F8FF",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
}

# ─── CSS personalizzato ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sfondo principale */
    .stApp { background-color: #F0F8FF; }

    /* Header titolo */
    .main-title {
        background: linear-gradient(135deg, #0077BE, #00A8E8);
        color: white;
        padding: 20px 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,119,190,0.3);
    }
    .main-title h1 { margin: 0; font-size: 2em; }
    .main-title p  { margin: 5px 0 0; opacity: 0.85; font-size: 1em; }

    /* Card squadra */
    .team-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 5px solid #0077BE;
        transition: transform 0.2s;
    }
    .team-card:hover { transform: translateY(-2px); }

    /* Podio classifica */
    .rank-1 { border-left-color: #FFD700 !important; background: linear-gradient(to right, #FFFDE7, white) !important; }
    .rank-2 { border-left-color: #C0C0C0 !important; background: linear-gradient(to right, #F5F5F5, white) !important; }
    .rank-3 { border-left-color: #CD7F32 !important; background: linear-gradient(to right, #FFF3E0, white) !important; }

    /* Badge punteggio */
    .score-badge {
        background: linear-gradient(135deg, #0077BE, #00A8E8);
        color: white;
        border-radius: 50px;
        padding: 8px 20px;
        font-size: 1.3em;
        font-weight: bold;
        display: inline-block;
    }

    /* Celle calendario */
    .cal-day {
        background: white;
        border-radius: 10px;
        padding: 8px;
        text-align: center;
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.2s;
        min-height: 60px;
    }
    .cal-day:hover { border-color: #0077BE; }
    .cal-day.has-events { background: #E3F2FD; border-color: #90CAF9; }
    .cal-day.today { border-color: #0077BE; font-weight: bold; }
    .cal-day.selected { background: #0077BE; color: white; }

    /* Pill regola punteggio */
    .rule-pill {
        display: inline-block;
        background: #E3F2FD;
        color: #0077BE;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 3px;
        font-size: 0.9em;
    }

    /* Alert personalizzato */
    .custom-success {
        background: #E8F5E9;
        border-left: 4px solid #27AE60;
        border-radius: 8px;
        padding: 12px 16px;
        color: #1B5E20;
        margin: 10px 0;
    }
    .custom-error {
        background: #FFEBEE;
        border-left: 4px solid #E74C3C;
        border-radius: 8px;
        padding: 12px 16px;
        color: #B71C1C;
        margin: 10px 0;
    }

    /* Sidebar */
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

    /* Bottoni principali */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s;
    }

    /* Nasconde elementi Streamlit non necessari */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# GESTIONE DATI
# ═══════════════════════════════════════════════════════════════════

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PHOTO_DIR, exist_ok=True)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ── Utenti ──────────────────────────────────────────────────────────
def load_users() -> Dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users_list = json.load(f)
            return {u["username"]: u for u in users_list}
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

# ── Squadre ─────────────────────────────────────────────────────────
def load_teams() -> Dict:
    if os.path.exists(TEAMS_FILE):
        with open(TEAMS_FILE, 'r', encoding='utf-8') as f:
            teams_list = json.load(f)
            return {t["team_id"]: t for t in teams_list}
    return {}

def save_teams(teams: Dict):
    ensure_dirs()
    with open(TEAMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(teams.values()), f, indent=2, ensure_ascii=False)

# ── Regole punteggio ────────────────────────────────────────────────
def load_scoring_rules() -> Dict:
    if os.path.exists(SCORING_RULES_FILE):
        with open(SCORING_RULES_FILE, 'r', encoding='utf-8') as f:
            rules_list = json.load(f)
            return {r["rule_id"]: r for r in rules_list}
    return {}

def save_scoring_rules(rules: Dict):
    ensure_dirs()
    with open(SCORING_RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(rules.values()), f, indent=2, ensure_ascii=False)

def init_scoring_rules():
    rules = load_scoring_rules()
    if not rules:
        for r in DEFAULT_SCORING_RULES:
            r["created_at"] = datetime.now().isoformat()
            r["is_active"] = True
            rules[r["rule_id"]] = r
        save_scoring_rules(rules)

# ── Voci punteggio ──────────────────────────────────────────────────
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
        "team_id": team_id,
        "rule_id": rule_id,
        "date": date_str,
        "points": points,
        "notes": notes,
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

# ── Foto squadra ────────────────────────────────────────────────────
def save_team_photo(team_id: str, uploaded_file) -> Optional[str]:
    ensure_dirs()
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    filename = f"{team_id}{ext}"
    path = os.path.join(PHOTO_DIR, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def get_team_photo_b64(photo_path: str) -> Optional[str]:
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as f:
            data = f.read()
        ext = os.path.splitext(photo_path)[1].lower().strip(".")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif"}.get(ext, "png")
        return f"data:image/{mime};base64,{base64.b64encode(data).decode()}"
    return None


# ═══════════════════════════════════════════════════════════════════
# AUTENTICAZIONE
# ═══════════════════════════════════════════════════════════════════

def login(username: str, password: str) -> bool:
    users = load_users()
    user = users.get(username)
    if user and user["password_hash"] == hash_password(password):
        users[username]["last_login"] = datetime.now().isoformat()
        save_users(users)
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.is_admin = user["is_admin"]
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_admin = False
    st.session_state.current_page = "classifica"


# ═══════════════════════════════════════════════════════════════════
# INIT SESSION STATE
# ═══════════════════════════════════════════════════════════════════

def init_session():
    defaults = {
        "logged_in": False,
        "username": None,
        "is_admin": False,
        "current_page": "classifica",
        "cal_year": datetime.now().year,
        "cal_month": datetime.now().month,
        "selected_date": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


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
            username = st.text_input("👤 Username", placeholder="Inserisci username")
            password = st.text_input("🔑 Password", type="password", placeholder="Inserisci password")
            submitted = st.form_submit_button("Accedi", use_container_width=True, type="primary")
            if submitted:
                if login(username, password):
                    st.rerun()
                else:
                    st.markdown('<div class="custom-error">❌ Username o password non corretti</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.caption("💡 Prima volta? Usa **admin / admin123** poi cambia la password nelle impostazioni.")


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

    sorted_teams = sorted(teams.values(), key=lambda t: t.get("total_score", 0), reverse=True)
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    rank_class = {0: "rank-1", 1: "rank-2", 2: "rank-3"}

    for i, team in enumerate(sorted_teams):
        medal = medals.get(i, f"#{i+1}")
        rclass = rank_class.get(i, "")
        photo_html = ""
        photo_b64 = get_team_photo_b64(team.get("photo_path"))
        if photo_b64:
            photo_html = f'<img src="{photo_b64}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;margin-right:15px;border:3px solid #0077BE;">'

        members = team.get("members", [])
        members_str = ", ".join(m["name"] for m in members) if members else "Nessun membro"

        st.markdown(f"""
        <div class="team-card {rclass}">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div style="display:flex;align-items:center;">
                    {photo_html}
                    <div>
                        <div style="font-size:1.4em;font-weight:bold;">{medal} {team['name']}</div>
                        <div style="color:#666;font-size:0.9em;">👥 {members_str}</div>
                    </div>
                </div>
                <div class="score-badge">⭐ {team.get('total_score', 0)} pt</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Calendario ──────────────────────────────────────────────────────
def page_calendario():
    st.markdown("""
    <div class="main-title">
        <h1>📅 Calendario Presenze</h1>
        <p>Registra presenze e assegna punteggi</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigazione mese
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("◀ Mese prec.", use_container_width=True):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with col2:
        month_names = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
                       "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        st.markdown(f"<h2 style='text-align:center;color:#0077BE;'>{month_names[st.session_state.cal_month]} {st.session_state.cal_year}</h2>", unsafe_allow_html=True)
    with col3:
        if st.button("Mese succ. ▶", use_container_width=True):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    # Ottieni dati del mese
    month_entries = get_entries_for_month(st.session_state.cal_year, st.session_state.cal_month)
    days_with_events = set(e["date"] for e in month_entries)

    # Intestazioni giorni
    day_names = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    cols = st.columns(7)
    for i, d in enumerate(day_names):
        with cols[i]:
            color = "#E74C3C" if i >= 5 else "#0077BE"
            st.markdown(f"<div style='text-align:center;font-weight:bold;color:{color};padding:8px 0;'>{d}</div>", unsafe_allow_html=True)

    # Griglia calendario
    cal = calendar.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)
    today = date.today()

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("<div style='min-height:55px;'></div>", unsafe_allow_html=True)
                else:
                    date_str = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                    is_today = (date(st.session_state.cal_year, st.session_state.cal_month, day) == today)
                    has_events = date_str in days_with_events
                    is_selected = st.session_state.selected_date == date_str

                    bg = "#0077BE" if is_selected else ("#E3F2FD" if has_events else "white")
                    txt_color = "white" if is_selected else ("black")
                    border = "3px solid #0077BE" if is_today else ("2px solid #90CAF9" if has_events else "1px solid #eee")
                    dot = "🔵" if has_events else ""

                    if st.button(f"{day}\n{dot}", key=f"day_{date_str}", use_container_width=True):
                        st.session_state.selected_date = date_str
                        st.rerun()

    # Sezione data selezionata
    if st.session_state.selected_date:
        st.markdown("---")
        sel_date = st.session_state.selected_date
        day_entries = get_entries_for_date(sel_date)
        teams = load_teams()
        rules = load_scoring_rules()

        st.markdown(f"### 📌 {sel_date}")

        # Mostra eventi esistenti
        if day_entries:
            st.markdown("**Attività registrate:**")
            for entry in day_entries:
                team_name = teams.get(entry["team_id"], {}).get("name", entry["team_id"])
                rule_name = rules.get(entry["rule_id"], {}).get("name", entry["rule_id"])
                st.markdown(f'<span class="rule-pill">🏊 {team_name} • {rule_name} • +{entry["points"]}pt</span>', unsafe_allow_html=True)
            st.markdown("")

        # Form assegna punteggio (solo admin)
        if st.session_state.is_admin and teams and rules:
            with st.expander("➕ Assegna Punteggio", expanded=not bool(day_entries)):
                with st.form(f"score_form_{sel_date}"):
                    team_options = {t["name"]: tid for tid, t in teams.items()}
                    rule_options = {r["name"]: rid for rid, r in rules.items() if r.get("is_active", True)}

                    selected_team_name = st.selectbox("🏊 Squadra", list(team_options.keys()))
                    selected_rule_name = st.selectbox("⭐ Tipo attività", list(rule_options.keys()))
                    notes = st.text_input("📝 Note (opzionale)")

                    if selected_rule_name:
                        rule_id = rule_options[selected_rule_name]
                        pts = rules[rule_id]["points"]
                        st.info(f"Punti assegnati: **+{pts}**")

                    if st.form_submit_button("✅ Assegna Punteggio", type="primary", use_container_width=True):
                        team_id = team_options[selected_team_name]
                        rule_id = rule_options[selected_rule_name]
                        if add_score_entry(team_id, rule_id, sel_date, notes):
                            st.success("✅ Punteggio assegnato!")
                            st.rerun()
        elif not st.session_state.is_admin:
            st.caption("🔒 Solo gli admin possono assegnare punteggi.")


# ── Squadre ─────────────────────────────────────────────────────────
def page_squadre():
    st.markdown("""
    <div class="main-title">
        <h1>👥 Gestione Squadre</h1>
        <p>Crea e gestisci le squadre</p>
    </div>
    """, unsafe_allow_html=True)

    teams = load_teams()

    # ─ Crea nuova squadra (solo admin) ─
    if st.session_state.is_admin:
        with st.expander("➕ Crea Nuova Squadra", expanded=not bool(teams)):
            with st.form("new_team_form"):
                col1, col2 = st.columns(2)
                with col1:
                    team_id = st.text_input("ID Squadra (es: team_rossi)", placeholder="team_rossi")
                with col2:
                    team_name = st.text_input("Nome Squadra", placeholder="I Rossi")
                photo = st.file_uploader("📷 Foto squadra (opzionale)", type=["jpg", "jpeg", "png"])

                if st.form_submit_button("✅ Crea Squadra", type="primary", use_container_width=True):
                    if not team_id or not team_name:
                        st.error("❌ Compila ID e Nome squadra.")
                    elif team_id in teams:
                        st.error("❌ ID già esistente.")
                    else:
                        photo_path = None
                        if photo:
                            photo_path = save_team_photo(team_id, photo)
                        teams[team_id] = {
                            "team_id": team_id,
                            "name": team_name,
                            "photo_path": photo_path,
                            "members": [],
                            "total_score": 0,
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat()
                        }
                        save_teams(teams)
                        st.success(f"✅ Squadra **{team_name}** creata!")
                        st.rerun()

    # ─ Lista squadre ─
    if not teams:
        st.info("🏊 Nessuna squadra ancora.")
        return

    for team_id, team in teams.items():
        with st.expander(f"🏊 {team['name']} — ⭐ {team.get('total_score', 0)} pt"):
            col1, col2 = st.columns([1, 3])
            with col1:
                photo_b64 = get_team_photo_b64(team.get("photo_path"))
                if photo_b64:
                    st.markdown(f'<img src="{photo_b64}" style="width:120px;height:120px;border-radius:12px;object-fit:cover;">', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="width:120px;height:120px;background:#E3F2FD;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:3em;">🏊</div>', unsafe_allow_html=True)

                if st.session_state.is_admin:
                    new_photo = st.file_uploader("Cambia foto", type=["jpg","jpeg","png"], key=f"photo_{team_id}")
                    if new_photo:
                        path = save_team_photo(team_id, new_photo)
                        teams[team_id]["photo_path"] = path
                        save_teams(teams)
                        st.rerun()

            with col2:
                st.markdown(f"**ID:** `{team_id}`")
                members = team.get("members", [])
                st.markdown(f"**Membri ({len(members)}):**")

                if members:
                    for m in members:
                        col_m, col_btn = st.columns([4, 1])
                        with col_m:
                            st.markdown(f"• {m['name']} _{m.get('role', 'membro')}_")
                        with col_btn:
                            if st.session_state.is_admin:
                                if st.button("🗑", key=f"del_member_{team_id}_{m['name']}"):
                                    teams[team_id]["members"] = [x for x in members if x["name"] != m["name"]]
                                    save_teams(teams)
                                    st.rerun()
                else:
                    st.caption("Nessun membro")

                if st.session_state.is_admin:
                    with st.form(f"add_member_{team_id}"):
                        col_a, col_b, col_c = st.columns([3, 2, 1])
                        with col_a:
                            new_member = st.text_input("Nuovo membro", key=f"nm_{team_id}", label_visibility="collapsed", placeholder="Nome membro")
                        with col_b:
                            new_role = st.selectbox("Ruolo", ["membro", "capitano", "vice"], key=f"nr_{team_id}", label_visibility="collapsed")
                        with col_c:
                            if st.form_submit_button("➕"):
                                if new_member:
                                    if any(m["name"] == new_member for m in members):
                                        st.error("Membro già presente")
                                    else:
                                        teams[team_id]["members"].append({
                                            "name": new_member,
                                            "role": new_role,
                                            "joined_at": datetime.now().isoformat()
                                        })
                                        save_teams(teams)
                                        st.rerun()

            # Elimina squadra
            if st.session_state.is_admin:
                st.markdown("---")
                if st.button(f"🗑️ Elimina squadra {team['name']}", key=f"del_team_{team_id}", type="secondary"):
                    del teams[team_id]
                    save_teams(teams)
                    st.rerun()


# ── Admin ────────────────────────────────────────────────────────────
def page_admin():
    st.markdown("""
    <div class="main-title">
        <h1>⚙️ Pannello Admin</h1>
        <p>Gestione regole di punteggio e statistiche</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⭐ Regole Punteggio", "📊 Statistiche", "👤 Utenti"])

    # ─── Tab Regole ───
    with tab1:
        rules = load_scoring_rules()
        st.markdown("### Regole attive")
        for rule_id, rule in rules.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown(f'<span class="rule-pill">⭐ {rule["name"]}</span>', unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{rule['points']} pt**")
            with col3:
                active = st.checkbox("Attiva", value=rule.get("is_active", True), key=f"active_{rule_id}")
                if active != rule.get("is_active", True):
                    rules[rule_id]["is_active"] = active
                    save_scoring_rules(rules)
                    st.rerun()
            with col4:
                if st.button("🗑", key=f"del_rule_{rule_id}"):
                    del rules[rule_id]
                    save_scoring_rules(rules)
                    st.rerun()

        st.markdown("---")
        st.markdown("### ➕ Nuova Regola")
        with st.form("new_rule_form"):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                r_name = st.text_input("Nome regola")
            with col2:
                r_points = st.number_input("Punti", min_value=1, max_value=100, value=1)
            with col3:
                r_desc = st.text_input("Descrizione (opzionale)")
            if st.form_submit_button("✅ Aggiungi", type="primary"):
                if r_name:
                    r_id = r_name.lower().replace(" ", "_")
                    if r_id in rules:
                        st.error("Regola già esistente")
                    else:
                        rules[r_id] = {
                            "rule_id": r_id,
                            "name": r_name,
                            "points": r_points,
                            "description": r_desc,
                            "created_at": datetime.now().isoformat(),
                            "is_active": True
                        }
                        save_scoring_rules(rules)
                        st.success("✅ Regola aggiunta!")
                        st.rerun()

    # ─── Tab Statistiche ───
    with tab2:
        teams = load_teams()
        entries = load_score_entries()
        rules = load_scoring_rules()

        col1, col2, col3 = st.columns(3)
        col1.metric("🏊 Squadre", len(teams))
        col2.metric("📅 Attività Totali", len(entries))
        col3.metric("⭐ Punti Assegnati", sum(e["points"] for e in entries))

        if entries and teams:
            st.markdown("---")
            st.markdown("### 📊 Punteggi per squadra")
            sorted_teams = sorted(teams.values(), key=lambda t: t.get("total_score", 0), reverse=True)
            for t in sorted_teams:
                score = t.get("total_score", 0)
                max_score = max(tt.get("total_score", 0) for tt in teams.values()) or 1
                pct = score / max_score
                st.markdown(f"**{t['name']}** — {score} pt")
                st.progress(pct)

            st.markdown("---")
            st.markdown("### 📋 Ultimi 20 movimenti")
            recent = sorted(entries, key=lambda e: e["created_at"], reverse=True)[:20]
            for e in recent:
                team_name = teams.get(e["team_id"], {}).get("name", e["team_id"])
                rule_name = rules.get(e["rule_id"], {}).get("name", e["rule_id"])
                st.markdown(f"- `{e['date']}` · **{team_name}** · {rule_name} · +{e['points']}pt")

    # ─── Tab Utenti ───
    with tab3:
        users = load_users()
        st.markdown("### Utenti registrati")
        for uname, user in users.items():
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.markdown(f"**{uname}** {'👑 Admin' if user['is_admin'] else '👤 Utente'}")
            col2.markdown(f"Creato: {user['created_at'][:10]}")
            with col3:
                if uname != "admin" and st.button("🗑", key=f"del_user_{uname}"):
                    del users[uname]
                    save_users(users)
                    st.rerun()

        st.markdown("---")
        st.markdown("### ➕ Nuovo Utente")
        with st.form("new_user_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                n_username = st.text_input("Username")
            with col2:
                n_password = st.text_input("Password", type="password")
            with col3:
                n_admin = st.checkbox("Admin")
            if st.form_submit_button("✅ Crea Utente", type="primary"):
                if n_username and n_password:
                    if n_username in users:
                        st.error("Username già esistente")
                    else:
                        users[n_username] = {
                            "username": n_username,
                            "password_hash": hash_password(n_password),
                            "is_admin": n_admin,
                            "created_at": datetime.now().isoformat(),
                            "last_login": None
                        }
                        save_users(users)
                        st.success("✅ Utente creato!")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 🔑 Cambia Password")
        with st.form("change_pwd_form"):
            old_pwd = st.text_input("Password attuale", type="password")
            new_pwd = st.text_input("Nuova password", type="password")
            if st.form_submit_button("🔑 Cambia Password", type="primary"):
                cur_user = users.get(st.session_state.username)
                if cur_user and cur_user["password_hash"] == hash_password(old_pwd):
                    users[st.session_state.username]["password_hash"] = hash_password(new_pwd)
                    save_users(users)
                    st.success("✅ Password aggiornata!")
                else:
                    st.error("❌ Password attuale errata")


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════

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
            ("👥 Squadre", "squadre"),
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

    render_sidebar()

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
