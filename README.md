# 🏊 Pool Attendance App — Guida Deployment

## File inclusi
- `app.py` — app principale Streamlit
- `requirements.txt` — dipendenze Python
- `.streamlit/config.toml` — configurazione tema

---

## ✅ PASSO 1 — Crea account GitHub (gratis)
1. Vai su https://github.com e clicca **Sign up**
2. Inserisci email, password, username
3. Verifica email e accedi

## ✅ PASSO 2 — Crea il repository
1. Clicca il **+** in alto a destra → **New repository**
2. Nome: `pool-attendance-app`
3. Seleziona **Public**
4. Clicca **Create repository**

## ✅ PASSO 3 — Carica i file su GitHub
Dal tuo repository appena creato:
1. Clicca **uploading an existing file**
2. Trascina TUTTI i file dello zip (app.py, requirements.txt, la cartella .streamlit)
3. Clicca **Commit changes**

## ✅ PASSO 4 — Pubblica su Streamlit Cloud (gratis)
1. Vai su https://streamlit.io/cloud
2. Clicca **Sign up** → accedi con il tuo account GitHub
3. Clicca **New app**
4. Seleziona il tuo repository `pool-attendance-app`
5. Branch: `main`, File: `app.py`
6. Clicca **Deploy!**

⏱️ Attendi 2-3 minuti. Riceverai un link tipo:
`https://tuousername-pool-attendance-app.streamlit.app`

Quel link funziona su qualsiasi cellulare!

---

## 🔐 Credenziali default
- Username: `admin`
- Password: `admin123`

⚠️ **Cambia subito la password** dal pannello Admin → Utenti dopo il primo accesso!

---

## 💡 Note importanti
- I dati vengono salvati nel server di Streamlit Cloud
- Se l'app non viene visitata per 7 giorni, va in "sleep" (si risveglia al primo accesso)
- Per dati persistenti a lungo termine, considera Streamlit Community Cloud con GitHub Gist o un database esterno come Supabase
