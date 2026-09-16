import streamlit as st
import pandas as pd
import os
import logging
from datetime import datetime
from analyzer import analyze_denials, get_payer_breakdown, get_denial_code_breakdown, validate_columns, REQUIRED_COLS
from report_generator import generate_pdf
from email_drafter import draft_appeal_emails, generate_ai_appeal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("rcm")

MAX_UPLOAD_MB = 10
MAX_AI_EMAIL_ROWS = 25

st.set_page_config(
    page_title="RCM Denial Analyzer Pro",
    page_icon="🏥",
    layout="wide",
)

# ── MOTION-UI (pure CSS, respects prefers-reduced-motion) ────────
MOTION_CSS = """
<style>
@keyframes rcmFadeIn { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }
@keyframes rcmPulse { 0% { box-shadow: 0 0 0 0 rgba(39,174,96,0.55); } 70% { box-shadow: 0 0 0 12px rgba(39,174,96,0); } 100% { box-shadow: 0 0 0 0 rgba(39,174,96,0); } }
@keyframes rcmDots { 0%,80%,100% { opacity: 0.2; } 40% { opacity: 1; } }
@keyframes rcmShimmer { 0% { background-position: -400px 0; } 100% { background-position: 400px 0; } }

.rcm-header { animation: rcmFadeIn .45s ease-out both; background: linear-gradient(135deg,#1B3A6B 0%,#2C5282 100%); padding:22px 26px; border-radius:10px; margin-bottom:20px; box-shadow: 0 4px 12px rgba(27,58,107,0.15); }
.rcm-header h1 { color:#fff; margin:0; font-size:28px; letter-spacing:-0.5px; }
.rcm-header p { color:#BFDBFE; margin:4px 0 0; font-size:14px; }

[data-testid="stMetric"] { transition: transform .18s ease, box-shadow .18s ease; border-radius:8px; padding:8px; }
[data-testid="stMetric"]:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.08); }

.stButton>button { transition: transform .1s ease, box-shadow .18s ease; }
.stButton>button:active { transform: scale(0.97); }
.stButton>button[kind="primary"]:hover { box-shadow: 0 4px 14px rgba(27,58,107,0.35); }

div[data-testid="stAlert"][data-baseweb="notification"] { animation: rcmFadeIn .3s ease-out both; }
div[data-baseweb="notification"][kind="success"] { animation: rcmFadeIn .3s ease-out both, rcmPulse 1.4s ease-out 1; }

.stTabs [data-baseweb="tab-highlight"] { transition: left .25s cubic-bezier(.4,0,.2,1), width .25s cubic-bezier(.4,0,.2,1); }
.stTabs [data-baseweb="tab"] { transition: color .18s ease; }

.stProgress > div > div > div { background: linear-gradient(90deg,#1B3A6B,#27AE60); transition: width .35s ease; }

.rcm-skeleton { display:inline-block; }
.rcm-skeleton span { display:inline-block; width:8px; height:8px; margin:0 3px; border-radius:50%; background:#1B3A6B; animation: rcmDots 1.2s infinite ease-in-out both; }
.rcm-skeleton span:nth-child(1) { animation-delay:-0.32s; }
.rcm-skeleton span:nth-child(2) { animation-delay:-0.16s; }

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
</style>
"""
st.markdown(MOTION_CSS, unsafe_allow_html=True)

# ── HEADER ──────────────────────────────────────────────────────
st.markdown("""
<div class='rcm-header'>
    <h1>🏥 RCM Denial Analyzer Pro</h1>
    <p>AI-powered denial pattern analysis · Find hidden revenue in minutes</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    company_name = st.text_input("Practice / Company Name", value="Your Practice")
    api_key = st.text_input("Anthropic API Key", type="password",
                            value=st.session_state.get("api_key", os.getenv("ANTHROPIC_API_KEY", "")),
                            help="Get yours at console.anthropic.com")
    if api_key:
        # Per-session only — never write to os.environ (leaks across users on shared Streamlit)
        st.session_state["api_key"] = api_key

    st.markdown("---")
    st.warning(
        "⚠️ **HIPAA notice:** This app sends denial data to Anthropic's API. "
        "Ensure you have a signed BAA with Anthropic before uploading real PHI. "
        "Sample data is safe. Patient IDs are never sent in prompts."
    )
    phi_consent = st.checkbox("I confirm BAA is in place (or I'm using de-identified/sample data)",
                              value=st.session_state.get("phi_consent", False))
    st.session_state["phi_consent"] = phi_consent

    st.markdown("---")
    st.markdown("### 📋 Required Columns")
    st.markdown("""
- `claim_id`
- `patient_id`
- `payer`
- `denial_code`
- `denial_reason`
- `amount`
- `date`
- `procedure_code`
""")
    st.markdown("---")
    st.markdown("**💡 Denial Codes**")
    st.markdown("""
- **CO-4**: Timely Filing
- **CO-16**: Missing Info
- **CO-50**: Not Medically Necessary
- **CO-97**: Duplicate
- **PR-96**: Non-Covered
""")

# ── FILE UPLOAD ──────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📧 Appeal Emails", "📄 PDF Report"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader(
            "Upload EOB / Claims CSV or Excel",
            type=["csv", "xlsx"],
            help="Upload your denial report. Use sample_data/sample_eob.csv to try it out."
        )
    with col2:
        use_sample = st.button("📂 Load Sample Data", use_container_width=True)
        st.caption("Try with 50 demo claims")

    df = None

    if use_sample:
        sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_eob.csv")
        if os.path.exists(sample_path):
            df = pd.read_csv(sample_path)
            st.success(f"✅ Loaded {len(df)} sample claims")
        else:
            st.error("Sample file not found.")

    if uploaded:
        if uploaded.size > MAX_UPLOAD_MB * 1024 * 1024:
            st.error(f"File too large. Max {MAX_UPLOAD_MB} MB.")
        else:
            try:
                df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
                st.success(f"✅ Loaded {len(df)} claims from {uploaded.name}")
                log.info("upload rows=%d name=%s", len(df), uploaded.name)
            except Exception as e:
                st.error(f"Error reading file: {e}")

    if df is not None:
        try:
            validate_columns(df)
        except ValueError as e:
            st.error(str(e))
            st.stop()
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        st.session_state["df"] = df

        # Preview
        with st.expander("🔍 Data Preview", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"{len(df)} rows · {df['amount'].sum():,.2f} total denied $")

        # Quick stats
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Claims", len(df))
        m2.metric("Total Denied $", f"${df['amount'].sum():,.2f}")
        m3.metric("Unique Payers", df['payer'].nunique())
        m4.metric("Denial Codes", df['denial_code'].nunique())

        st.markdown("---")

        # Charts
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Top Denial Codes by Amount**")
            code_df = get_denial_code_breakdown(df)
            st.bar_chart(code_df.set_index("denial_code")["total_amount"].head(6))

        with col_b:
            st.markdown("**Denials by Payer**")
            payer_df = get_payer_breakdown(df)
            st.bar_chart(payer_df.set_index("payer")["total_amount"])

        st.markdown("---")

        # AI Analysis
        session_key = st.session_state.get("api_key", "")
        if not session_key:
            st.warning("⚠️ Add your Anthropic API key in the sidebar to run AI analysis.")
        elif not st.session_state.get("phi_consent"):
            st.warning("⚠️ Confirm HIPAA/BAA notice in sidebar before running AI analysis.")
        else:
            if st.button("🤖 Run AI Denial Analysis", type="primary", use_container_width=True):
                with st.spinner("Analyzing denial patterns with Claude AI..."):
                    try:
                        analysis = analyze_denials(df, api_key=session_key)
                        st.session_state["analysis"] = analysis
                        st.success("✅ Analysis complete!")
                    except Exception as e:
                        log.exception("analyze_denials failed")
                        st.error(f"Analysis error: {e}")

            if "analysis" in st.session_state:
                analysis = st.session_state["analysis"]
                summary = analysis.get("summary", {})

                st.markdown("### 📈 AI Analysis Results")
                r1, r2, r3 = st.columns(3)
                r1.metric("Denial Rate", f"{summary.get('denial_rate_pct', 0):.1f}%")
                r2.metric("Recoverable $", f"${summary.get('estimated_recoverable_amount', 0):,.0f}")
                r3.metric("Recovery Rate", f"{summary.get('recovery_rate_pct', 0):.0f}%")

                # Patterns
                patterns = analysis.get("top_patterns", [])
                if patterns:
                    st.markdown("#### 🎯 Top Denial Patterns")
                    pat_df = pd.DataFrame([{
                        "Code": p["denial_code"],
                        "Label": p["label"],
                        "Freq %": f"{p['frequency_pct']:.1f}%",
                        "Amount $": f"${p['total_amount']:,.0f}",
                        "Recoverable $": f"${p['recoverable_amount']:,.0f}",
                        "Recovery %": f"{p['recovery_probability_pct']:.0f}%",
                        "Priority": p["priority"],
                    } for p in patterns])
                    st.dataframe(pat_df, use_container_width=True)

                # Actions
                actions = analysis.get("immediate_actions", [])
                if actions:
                    st.markdown("#### ⚡ Immediate Actions")
                    for i, a in enumerate(actions, 1):
                        st.markdown(f"**{i}.** {a}")

                # 30-day plan
                plan = analysis.get("30_day_recovery_plan", "")
                if plan:
                    with st.expander("📅 30-Day Recovery Plan"):
                        st.write(plan)

with tab2:
    st.markdown("### 📧 Appeal Email Drafts")

    if "df" not in st.session_state:
        st.info("Upload claims data in the Analysis tab first.")
    else:
        df = st.session_state["df"]

        gen_mode = st.radio(
            "Generation Mode",
            ["Template-based (instant)", "AI-generated (requires API key)"],
            horizontal=True
        )

        use_ai = gen_mode == "AI-generated (requires API key)"

        if st.button("📝 Generate Appeal Emails", type="primary"):
            session_key = st.session_state.get("api_key", "")
            with st.spinner("Drafting appeal emails..."):
                if use_ai and not session_key:
                    st.warning("⚠️ Add Anthropic API key in sidebar for AI mode.")
                elif use_ai and not st.session_state.get("phi_consent"):
                    st.warning("⚠️ Confirm HIPAA/BAA notice in sidebar for AI mode.")
                elif use_ai:
                    if len(df) > MAX_AI_EMAIL_ROWS:
                        st.warning(f"AI mode capped at {MAX_AI_EMAIL_ROWS} rows (uploaded {len(df)}). Processing first {MAX_AI_EMAIL_ROWS}.")
                    emails = []
                    subset = df.head(MAX_AI_EMAIL_ROWS)
                    progress = st.progress(0.0)
                    for i, (_, row) in enumerate(subset.iterrows()):
                        claim_dict = row.to_dict()
                        try:
                            body = generate_ai_appeal(claim_dict, api_key=session_key)
                            emails.append({
                                "claim_id": row.get("claim_id"),
                                "denial_code": row.get("denial_code", ""),
                                "denial_label": row.get("denial_reason", ""),
                                "payer": row.get("payer"),
                                "amount": row.get("amount"),
                                "subject": f"Appeal — Claim #{row.get('claim_id')} — {row.get('denial_code')}",
                                "body": body,
                            })
                        except Exception as e:
                            log.warning("AI appeal row %s failed: %s", row.get("claim_id"), e)
                        progress.progress((i + 1) / len(subset))
                    progress.empty()
                    st.session_state["emails"] = emails
                    st.success(f"✅ Generated {len(emails)} AI appeal emails")
                else:
                    emails = draft_appeal_emails(df)
                    st.session_state["emails"] = emails
                    st.success(f"✅ Generated {len(emails)} appeal emails")

        if "emails" in st.session_state:
            emails = st.session_state["emails"]

            # Filter
            codes = list(set(e["denial_code"] for e in emails))
            selected_code = st.selectbox("Filter by Denial Code", ["All"] + sorted(codes))

            filtered = emails if selected_code == "All" else [e for e in emails if e["denial_code"] == selected_code]
            st.caption(f"Showing {len(filtered)} emails")

            for i, email in enumerate(filtered[:10]):
                with st.expander(f"📧 {email['claim_id']} — {email['payer']} — {email['denial_label']} — ${email['amount']:,.2f}"):
                    st.text(f"Subject: {email['subject']}")
                    st.markdown("---")
                    st.text_area("Email Body", email["body"], height=250, key=f"email_{i}", label_visibility="collapsed")

            # Download all
            if filtered:
                all_text = ("=" * 60 + "\n\n").join(
                    [f"CLAIM: {e['claim_id']} | {e['payer']} | {e['denial_code']}\nSUBJECT: {e['subject']}\n\n{e['body']}"
                     for e in filtered]
                )
                st.download_button(
                    "⬇️ Download All Emails (.txt)",
                    all_text,
                    file_name=f"appeal_emails_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

with tab3:
    st.markdown("### 📄 Generate PDF Report")

    if "analysis" not in st.session_state:
        st.info("Run AI Analysis in the Analysis tab first to generate a PDF report.")
    else:
        st.markdown("**Report will include:**")
        st.markdown("- Cover page with KPIs\n- Top denial patterns + fix actions\n- Payer breakdown\n- 30-day recovery plan")

        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Generating branded PDF report..."):
                try:
                    pdf_bytes = generate_pdf(
                        st.session_state["analysis"],
                        st.session_state["df"],
                        company_name=company_name
                    )
                    fname = f"denial_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=fname,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success(f"✅ Report ready: {fname}")
                except Exception as e:
                    st.error(f"PDF generation error: {e}")
                    st.exception(e)

# ── FOOTER ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#94A3B8;font-size:12px'>"
    "RCM Denial Analyzer Pro · AI-powered by Claude · Built for US medical billing teams"
    "</p>",
    unsafe_allow_html=True
)
