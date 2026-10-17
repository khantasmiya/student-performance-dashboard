
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #F5F7FB;
    color: #172033;
}
.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #172033 !important;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E7EBF3;
    padding: 20px 22px;
    border-radius: 16px;
    box-shadow: 0 4px 16px rgba(25, 40, 75, 0.045);
}
[data-testid="stMetricLabel"] {
    color: #64748B !important;
    font-size: 13px !important;
}
[data-testid="stMetricValue"] {
    color: #172033 !important;
    font-size: 30px !important;
    font-weight: 800 !important;
}
[data-testid="stPlotlyChart"] {
    background: white;
    border: 1px solid #E7EBF3;
    border-radius: 16px;
    padding: 8px;
}
div[data-testid="stFileUploader"] {
    background: white;
    border-radius: 12px;
}
div[data-testid="stSelectbox"] {
    background: transparent;
}
hr {
    border-color: #E7EBF3;
}
.small-caption {
    color: #64748B;
    font-size: 14px;
    margin-top: -12px;
}
</style>
""", unsafe_allow_html=True)

BG = "#FFFFFF"
GRID = "#E9EEF5"
TEXT = "#263247"
PALETTE = ["#6558E8", "#20B8A6", "#F4A340", "#EF6B83", "#4C91F0"]

def clean_columns(df):
    df.columns = [
        str(c).strip().replace("_", " ").replace("-", " ")
        for c in df.columns
    ]
    aliases = {
        "student id": "Student ID",
        "studentid": "Student ID",
        "gradeclass": "Grade Class",
        "grade class": "Grade Class",
        "studytimeweekly": "Study Time Weekly",
        "study time weekly": "Study Time Weekly",
        "parentaleducation": "Parental Education",
        "parental education": "Parental Education",
        "parentalsupport": "Parental Support",
        "parental support": "Parental Support",
        "extracurricular": "Extracurricular",
        "gpa": "GPA",
        "gender": "Gender",
        "age": "Age",
        "absences": "Absences",
    }
    df.columns = [
        aliases.get(c.lower().replace(" ", ""), aliases.get(c.lower(), c))
        for c in df.columns
    ]
    return df

def style_chart(fig, height=350):
    fig.update_layout(
        height=height,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        margin=dict(l=20, r=20, t=45, b=20),
        title=dict(font=dict(size=16, color=TEXT), x=0.02),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hoverlabel=dict(bgcolor="#172033", font_color="white")
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=GRID,
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False
    )
    return fig

# ---------- HEADER ----------
st.markdown(
    "<h1 style='margin-bottom:0'>📊 Student Performance Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='color:#64748B;font-size:15px;margin-top:5px'>"
    "Academic Insights&nbsp; • &nbsp;Study Habits&nbsp; • &nbsp;GPA"
    "</p>",
    unsafe_allow_html=True
)

# ---------- DATA ----------
uploaded = st.file_uploader(
    "Upload your Student Performance CSV",
    type=["csv"],
    help="Choose the CSV dataset you downloaded from Kaggle."
)

if uploaded is None:
    st.info(
        "👋 Upload your Student Performance CSV to create your dashboard. "
        "Use the dataset with Student ID, GPA, Grade Class, Age, Gender, "
        "Study Time Weekly and Absences columns."
    )
    st.markdown("### Your dashboard will include")
    a, b, c = st.columns(3)
    a.markdown("**📌 KPI cards**\n\nTotal students, average GPA, study time and grade classes.")
    b.markdown("**📈 Performance charts**\n\nGPA distribution, study habits and grade comparisons.")
    c.markdown("**🎛️ Interactive filters**\n\nExplore student groups by gender, age and parental support.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
    df = clean_columns(df)
except Exception as e:
    st.error(f"Could not read this CSV: {e}")
    st.stop()

required = ["GPA"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error("This file is missing the GPA column. Please upload the correct dataset.")
    st.write("Columns found:", list(df.columns))
    st.stop()

for col in ["GPA", "Age", "Absences", "Study Time Weekly"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["GPA"]).copy()

if df.empty:
    st.error("No valid GPA data was found in this CSV.")
    st.stop()

# ---------- FILTERS ----------
st.markdown("### Explore your data")
filter_cols = st.columns(4)
filtered = df.copy()

filter_specs = [
    ("Gender", "All genders"),
    ("Grade Class", "All grade classes"),
    ("Age", "All ages"),
    ("Parental Support", "All support levels")
]

for i, (col, label) in enumerate(filter_specs):
    if col in filtered.columns:
        with filter_cols[i]:
            values = sorted(
                filtered[col].dropna().unique().tolist(),
                key=lambda x: str(x)
            )
            selected = st.selectbox(
                label,
                ["All"] + values,
                key=f"filter_{col}"
            )
        if selected != "All":
            filtered = filtered[filtered[col] == selected]
    else:
        with filter_cols[i]:
            st.selectbox(label, ["Not available"], disabled=True, key=f"missing_{col}")

if filtered.empty:
    st.warning("No students match these filters. Change a filter to see results.")
    st.stop()

# ---------- KPI CARDS ----------
total = len(filtered)
avg_gpa = filtered["GPA"].mean()
avg_study = (
    filtered["Study Time Weekly"].mean()
    if "Study Time Weekly" in filtered.columns else np.nan
)
grade_count = (
    filtered["Grade Class"].nunique()
    if "Grade Class" in filtered.columns else 0
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Total Students", f"{total:,}")
k2.metric("🎓 Average GPA", f"{avg_gpa:.2f} / 4.0")
k3.metric(
    "📚 Avg Weekly Study",
    f"{avg_study:.1f} hrs" if pd.notna(avg_study) else "N/A"
)
k4.metric("🏷️ Grade Classes", str(grade_count))

st.markdown("---")

# ---------- ROW 1: SCATTER + DONUT ----------
left, right = st.columns([1.55, 1])

with left:
    st.markdown("### 📈 Study Time vs GPA")
    if {"Study Time Weekly", "GPA"}.issubset(filtered.columns):
        scatter_data = filtered.dropna(subset=["Study Time Weekly", "GPA"])
        color_col = "Gender" if "Gender" in scatter_data.columns else None
        fig = px.scatter(
            scatter_data,
            x="Study Time Weekly",
            y="GPA",
            color=color_col,
            color_discrete_sequence=PALETTE,
            hover_data=[
                c for c in ["Student ID", "Age", "Absences", "Grade Class"]
                if c in scatter_data.columns
            ],
            opacity=0.68,
            render_mode="webgl"
        )
        fig.update_traces(marker=dict(size=7))
        fig.update_layout(
            xaxis_title="Study time per week (hours)",
            yaxis_title="GPA",
            yaxis_range=[0, max(4.2, float(filtered["GPA"].max()) + 0.2)]
        )
        st.plotly_chart(style_chart(fig, 380), use_container_width=True)
    else:
        st.warning("Study Time Weekly column is unavailable.")

with right:
    st.markdown("### 🍩 Grade Class Distribution")
    if "Grade Class" in filtered.columns:
        counts = (
            filtered["Grade Class"].astype(str)
            .value_counts().rename_axis("Grade Class")
            .reset_index(name="Students")
        )
        fig = px.pie(
            counts,
            names="Grade Class",
            values="Students",
            hole=0.62,
            color_discrete_sequence=PALETTE
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate="Grade class %{label}<br>Students: %{value}<extra></extra>",
            marker=dict(line=dict(color=BG, width=3))
        )
        fig.add_annotation(
            text=f"<b>{total:,}</b><br><span style='font-size:11px'>Students</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color=TEXT)
        )
        st.plotly_chart(style_chart(fig, 380), use_container_width=True)
    else:
        st.warning("Grade Class column is unavailable.")

# ---------- ROW 2: GPA BY CLASS + HISTOGRAM ----------
left, right = st.columns(2)

with left:
    st.markdown("### 📊 Average GPA by Grade Class")
    if "Grade Class" in filtered.columns:
        grouped = (
            filtered.groupby("Grade Class", as_index=False)["GPA"]
            .mean().sort_values("Grade Class")
        )
        grouped["Grade Class"] = grouped["Grade Class"].astype(str)
        fig = px.bar(
            grouped,
            x="Grade Class",
            y="GPA",
            color="Grade Class",
            color_discrete_sequence=PALETTE,
            text_auto=".2f"
        )
        fig.update_traces(
            marker_line_width=0,
            textposition="outside",
            cliponaxis=False
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="Grade Class",
            yaxis_title="Average GPA",
            yaxis_range=[0, 4.4]
        )
        st.plotly_chart(style_chart(fig, 340), use_container_width=True)
    else:
        st.warning("Grade Class column is unavailable.")

with right:
    st.markdown("### 📉 GPA Distribution")
    fig = px.histogram(
        filtered,
        x="GPA",
        nbins=20,
        color_discrete_sequence=["#6558E8"],
        opacity=0.9
    )
    fig.update_traces(
        marker_line_color=BG,
        marker_line_width=1
    )
    fig.update_layout(
        xaxis_title="GPA",
        yaxis_title="Number of students",
        bargap=0.08
    )
    st.plotly_chart(style_chart(fig, 340), use_container_width=True)

# ---------- ROW 3: GENDER + CORRELATION ----------
left, right = st.columns(2)

with left:
    st.markdown("### 👥 Students by Gender")
    if "Gender" in filtered.columns:
        gender_counts = (
            filtered["Gender"].astype(str)
            .value_counts().rename_axis("Gender")
            .reset_index(name="Students")
        )
        fig = px.bar(
            gender_counts,
            x="Students",
            y="Gender",
            orientation="h",
            color="Gender",
            color_discrete_sequence=PALETTE,
            text="Students"
        )
        fig.update_traces(
            textposition="outside",
            cliponaxis=False
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="Number of students",
            yaxis_title="",
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(style_chart(fig, 320), use_container_width=True)
    else:
        st.warning("Gender column is unavailable.")

with right:
    st.markdown("### 🔥 Correlation Heatmap")
    numeric_candidates = [
        "Study Time Weekly", "Absences", "GPA", "Age"
    ]
    numeric_cols = [
        c for c in numeric_candidates
        if c in filtered.columns
        and pd.api.types.is_numeric_dtype(filtered[c])
    ]
    if len(numeric_cols) >= 2:
        corr = filtered[numeric_cols].corr()
        fig = go.Figure(
            data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.index,
                zmin=-1,
                zmax=1,
                colorscale=[
                    [0, "#EF6B83"],
                    [0.5, "#F4F6FA"],
                    [1, "#6558E8"]
                ],
                text=np.round(corr.values, 2),
                texttemplate="%{text:.2f}",
                hovertemplate="%{y} vs %{x}: %{z:.2f}<extra></extra>",
                colorbar=dict(title="Correlation")
            )
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(style_chart(fig, 320), use_container_width=True)
    else:
        st.info("At least two numeric columns are needed for the heatmap.")

# ---------- DATA TABLE ----------
with st.expander("🔎 View filtered student records"):
    st.caption(f"Showing {len(filtered):,} records after filters.")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_student_performance.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Student Performance Dashboard • Built with Streamlit and Plotly")

