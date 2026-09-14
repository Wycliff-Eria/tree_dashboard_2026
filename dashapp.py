import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Tree Program Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

[data-testid="stMetric"] {
    background-color: black;
    border: 1px solid #dddddd;
    padding: 15px;
    border-radius: 10px;
}

.dashboard-title {
    font-size: 35px;
    font-weight: bold;
}

.dashboard-subtitle {
    font-size: 17px;
    color: #666666;

.header {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: white;
        padding: 10px 20px;
        border-bottom: 1px solid #ddd;



}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TITLE
# ============================================================
col1, col2 = st.columns([5, 1])


with col2:
    st.image("oaf_logo.png", width=200)


st.markdown(
    '<div class="dashboard-title">Tree Program Monitoring Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Monitoring household participation, tree distribution, planting and survival'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

# ============================================================
# DATA UPLOAD
# ============================================================

st.sidebar.header("📂 Upload_Dataset here")

uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is None:

    st.info(
        "👈 Please upload your dataset from the sidebar to start the dashboard."
    )

    st.markdown("""
    ### Dashboard features

    Once you upload the data, this dashboard will show:

    - Total respondents
    - Program participants
    - Tree recipients
    - Trees planted
    - Tree survival
    - Results by district
    - Results by site
    - Results by tree species
    - Training participation
    - Respondent characteristics
    """)

    st.stop()

# ============================================================
# LOAD DATA
# ============================================================
st.cache_data

try:

    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file,index_col=0)

except Exception as e:

    st.error(f"Error loading file: {e}")
    st.stop()

# preview data

def drop_columns(df, columns):
    """
    Drop specified columns from a DataFrame.
    """
    df = df.drop(columns=columns, errors='ignore')
    return df

columns_to_drop = [
    "first_name",
    "last_name",
    "other_name",
    "respondent_phone_2",
    "respondent_phone_3",
    "village_dem",
    "respondent_location",
    "survey_audio_1",
    "survey_audio_2",
    "survey_audio_3",
    "survey_audio_4",
    "survey_audio_5",
    "fieldofficer",
    "name",
    "respondent_phone"
]

df = drop_columns(df, columns_to_drop)

df = df[df['username'].str.strip().str.lower() != 'mel_pilot']

st.subheader("Data preview")
with st.expander("View data records"):
    st.write(df.head(3))
    st.write(df.shape)

#=====================
# IMPUTE COLUMNS
#=====================

#fillna in diastrict column using username mapping
district_map = {
    "gerald_mwidu": "kamuli",
    "levi_mudaasi": "kamuli",
    "eria_wandera": "kamuli",
    "betty_namuwaya": "kamuli",
    "aggrey_kalogo": "kamuli",
    "frank_mununuzi": "iganga",
    "sharif_makayi": "iganga",
    "julius_kitezaala": "kamuli",
    "daniel_kakaire": "iganga",
    "simon_wagabaza": "jinja",
    "fred_kibeibuka": "buikwe",
    "christine_nagudi": "buikwe",
    "christine_nagudi": "mukono",
    "tom_mwoko": "kamuli",
    "robert_ssentongo":"mukono",
    "faluku_malikwe":"kamuli",
    "denis_opere":"mukono"
}

df["district"] = df["district"].fillna(
    df["username"].map(district_map)
)

#Key functions
def convert_num(data,column_name):
    if column_name not in data.columns:
            return data
    data[column_name] = pd.to_numeric(data[column_name], errors='coerce')
    data[column_name] = data[column_name].fillna(0)
    


def clean_up(data, column_name):

    if column_name not in data.columns:
        return data

    data[column_name] = (
        data[column_name]
        .astype("string")
        .str.lower()
        .str.strip()
        .replace("---", pd.NA)
        
    )
    # Remove rows where this column is NA
    data = data.dropna(subset=[column_name])

    return data

# ============================================================
#convert_num(df, "oaf_grev_planted_n") --> to numeric
#clean_up(df, "oaf_grev_planted_n") --> clean up txt data
# ============================================================

# ============================================================
# CLEAN DATA
# ============================================================

df=clean_up(df, "resp_gender") 
df=clean_up(df, "lr2026trees_adoption_complete")   

# filter data
#lr2026trees_adoption_complete,consent,gender,district,program_participant,
st.sidebar.subheader("Filters")

selected_district=st.sidebar.multiselect(
    "Select district", options=df['district'].unique(),default=df["district"].unique()
)

selected_gender=st.sidebar.multiselect(
    "Select gender", options=df["resp_gender"].unique(),default=df["resp_gender"].unique()
)

selected_program=st.sidebar.multiselect(
    "Select program", options=df['program_participant'].unique(),default=df["program_participant"].unique()
)

selected_status=st.sidebar.multiselect(
    "Select form status", options=df['lr2026trees_adoption_complete'].unique(),default=df["lr2026trees_adoption_complete"].unique()
)
#apply filters
filtered_df=df[
    (df["district"].isin(selected_district))&
    (df["resp_gender"].isin(selected_gender))&
    (df["program_participant"].isin(selected_program))&
    (df["lr2026trees_adoption_complete"].isin(selected_status))
]

st.subheader("Filtered Data Preview")

with st.expander("View filtered records"):
    st.write(filtered_df.head(3))
    st.write(filtered_df.shape)

# Convert numeric columns

numeric_columns = [

    "resp_age",
    "n_hh",
    "n_hh_youth",
    "land_owned_acres_calc",

    "oaf_grev_planted_n",
    "oaf_alb_planted_n",
    "oaf_faid_planted_n",

    "oaf_grev_received_n",
    "oaf_alb_received_n",
    "oaf_faid_received_n",
    

    "d_tot_grev_rpt_tot_n_surviving",
    "d_tot_alb_rpt_tot_n_surviving",
    "d_tot_faid_rpt_tot_n_surviving"

    "oaf_grevcount_plot1_n"
    "oaf_grevcount_plot2_n"
    "oaf_grevcount_plot3_n"
    "nonoaf_grevcount_plot1_n"
    "nonoaf_grevcount_plot2_n"
    "nonoaf_grevcount_plot3_n"

    "oaf_albcount_plot1_n"
    "oaf_albcount_plot2_n"
    "oaf_albcount_plot3_n"
    "nonoaf_albcount_plot1_n"
    "nonoaf_albcount_plot2_n"
    "nonoaf_albcount_plot3_n"

    "oaf_faidcount_plot1_n"
    "oaf_faidcount_plot2_n"
    "oaf_faidcount_plot3_n"
    "nonoaf_faidcount_plot1_n"
    "nonoaf_faidcount_plot2_n"
    "nonoaf_faidcount_plot3_n"
    
]

for col in numeric_columns:

    if col in filtered_df.columns:

        filtered_df[col] = pd.to_numeric(
            filtered_df[col],
            errors="coerce"
        )

#calculations for key matrics

total_respondents = len(filtered_df)
# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_sum(data, column):

    if column not in data.columns:
        return 0

    return data[column].fillna(0).sum()


def safe_count(data, column):

    if column not in data.columns:
        return 0

    return data[column].notna().sum()
#trees received
grev_received=safe_sum(filtered_df,"oaf_grev_received_n")
alb_received=safe_sum(filtered_df,"oaf_alb_received_n")
faid_received=safe_sum(filtered_df,"oaf_faid_received_n")

total_received = (
    grev_received +
    alb_received +
    faid_received
)

#trees planted
grev_planted=safe_sum(filtered_df,"oaf_grev_planted_n")
alb_planted=safe_sum(filtered_df,"oaf_alb_planted_n")
faid_planted=safe_sum(filtered_df,"oaf_faid_planted_n")

total_planted=(
    grev_planted +
    alb_planted +
    faid_planted
)

#tree surviving


def calculate_total(data, columns):
    existing_columns = [col for col in columns if col in data.columns]

    return int(
        data[existing_columns]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .sum()
        .sum()
    )

#grev
grev_surviving = calculate_total(
    filtered_df,
    [   
        "d_tot_grev_rpt_tot_n_surviving",
        "oaf_grevcount_plot1_n",
        "oaf_grevcount_plot2_n",
        "oaf_grevcount_plot3_n"
    ]
)

#alb
alb_surviving = calculate_total(
    filtered_df,
    [   
        "d_tot_alb_rpt_tot_n_surviving",
        "oaf_albcount_plot1_n",
        "oaf_albcount_plot2_n",
        "oaf_albcount_plot3_n"
    ]
)

#faid
faid_surviving = calculate_total(
    filtered_df,
    [   
        "d_tot_faid_rpt_tot_n_surviving",
        "oaf_faidcount_plot1_n",
        "oaf_faidcount_plot2_n",
        "oaf_faidcount_plot3_n"
    ]
)

total_surviving = grev_surviving + alb_surviving + faid_surviving

#survival rate
survival_rate = (
    (total_surviving / total_planted) * 100
    if total_planted > 0 else 0
)

#key metrics
st.subheader("Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Respondents",
        value=total_respondents
    )

with col2:
    st.metric(
        label="Total Trees Received",
        value=round(total_received)
    )

with col3:
    st.metric(
        label="Total Trees Planted",
        value=round(total_planted)
    )

with col4:
    st.metric(
        label="Total Trees Surviving",
        value=round(total_surviving)
    )

with col5:
    st.metric(
        label="Survival Rate",
        value=f"{survival_rate:.1f}%"
    )

st.divider()


# ============================================================
# TREE SPECIES SUMMARY
# ============================================================

species_data = pd.DataFrame({

    "Species": [
        "Grevillea",
        "Albizia",
        "Faidherbia"
    ],

    "Received": [
        grev_received,
        alb_received,
        faid_received
    ],

    "Planted": [
        grev_planted,
        alb_planted,
        faid_planted
    ],

    "Surviving": [
        grev_surviving,
        alb_surviving,
        faid_surviving
    ]
})

#visualizations 

st.subheader("Tree Distribution and Survival")

col1, col2 = st.columns(2)


with col1:

    fig = px.bar(
        species_data,
        x="Species",
        y=["Received", "Planted", "Surviving"],
        barmode="group",
        title="Trees Received, Planted and Surviving",
        labels={
            "value": "Number of Trees",
            "variable": "Measure"
        }
    )

    fig.update_layout(
        legend_title_text="",
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    survival_species = species_data.copy()

    survival_species["Survival Rate"] = (
        survival_species["Surviving"] /
        survival_species["Planted"].replace(0, pd.NA)
    ) * 100

    survival_species["Survival Rate"] = (
        survival_species["Survival Rate"]
        .fillna(0)
    )

    fig = px.bar(
        survival_species,
        x="Species",
        y="Survival Rate",
        text="Survival Rate",
        title="Survival Rate by Species",
        labels={
            "Survival Rate": "Survival Rate (%)"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_range=[
            0,
            max(100, survival_species["Survival Rate"].max() + 10)
        ],
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# LOCATION ANALYSIS
# ============================================================

st.subheader("Geographic Analysis")

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# District respondents
# ------------------------------------------------------------
convert_num(filtered_df, "oaf_grev_planted_n")
convert_num(filtered_df, "oaf_alb_planted_n")
convert_num(filtered_df, "oaf_faid_planted_n")

grev_pltd_district=(filtered_df.groupby("district")[["oaf_grev_planted_n", "oaf_alb_planted_n", "oaf_faid_planted_n"]]).sum().astype(int).reset_index()

grev_pltd_district = grev_pltd_district.rename(columns={
    "oaf_grev_planted_n": "Grevillea Planted",
    "oaf_alb_planted_n": "Albizia Planted",
    "oaf_faid_planted_n": "Faidherbia Planted"
})

with col1:

    if "district" in filtered_df.columns:

        district_data = (
            filtered_df["district"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        district_data.columns = [
            "District",
            "Respondents"
        ]

        fig = px.bar(
            district_data,
            x="District",
            y="Respondents",
            title="Respondents by District",
            text="Respondents"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


with col2:

    fig = px.bar(
    grev_pltd_district,
    x="district",
    y=[
        "Grevillea Planted",
        "Albizia Planted",
        "Faidherbia Planted"
    ],
    barmode="group",
    title="Planted Trees by District",
    labels={
        "district": "District",
        "value": "Number of Trees planted",
        "variable": "Tree Type"
    }
)

    fig.update_layout(
            legend_title_text="",
            height=450
)

    st.plotly_chart(
            fig,
            use_container_width=True
        )


st.subheader("Program Participation")

col1, col2 = st.columns(2)


with col1:

    if "program_participant" in filtered_df.columns:

        participant_data = (
            filtered_df["program_participant"]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .reset_index()
        )

        participant_data.columns = [
            "Participation",
            "Respondents"
        ]

        fig = px.pie(
            participant_data,
            names="Participation",
            values="Respondents",
            title="Program Participation"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


with col2:

    if "training" in filtered_df.columns:

        training_data = (
            filtered_df["training"]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .reset_index()
        )

        training_data.columns = [
            "Training",
            "Respondents"
        ]

        fig = px.pie(
            training_data,
            names="Training",
            values="Respondents",
            title="Training Participation"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ============================================================
# RESPONDENT DEMOGRAPHICS
# ============================================================

st.subheader("Respondent Characteristics")

col1, col2 = st.columns([1, 1], gap="medium")


with col1:

    if "resp_gender" in filtered_df.columns:

        gender_data = (
            filtered_df["resp_gender"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        gender_data.columns = [
            "Gender",
            "Respondents"
        ]

        fig = px.bar(
            gender_data,
            x="Gender",
            y="Respondents",
            title="Respondents by Gender",
            text="Respondents"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


with col2:

    if "resp_age" in filtered_df.columns:

        age_data = filtered_df[
            "resp_age"
        ].dropna()

        if len(age_data) > 0:

            fig = px.histogram(
                age_data,
                x="resp_age",
                nbins=20,
                title="Age Distribution",
                labels={
                    "resp_age": "Age"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# LAND OWNERSHIP
# ============================================================

st.subheader("Land Ownership")

col1, col2 = st.columns(2)


with col1:

    if "hh_owns_land" in filtered_df.columns:

        land_data = (
            filtered_df["hh_owns_land"]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .reset_index()
        )

        land_data.columns = [
            "Land Ownership",
            "Households"
        ]

        fig = px.pie(
            land_data,
            names="Land Ownership",
            values="Households",
            title="Households Owning Land",
            hole=0.5
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )




with col2:

    if "more_farmplaces_planttrees" in filtered_df.columns:

        land_data2 = (
            filtered_df["more_farmplaces_planttrees"]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .reset_index()
        )

        land_data2.columns = [
            "more_farmplaces_planttrees",
            "Households"
        ]

        fig = px.pie(
            land_data2,
            names="more_farmplaces_planttrees",
            values="Households",
            title="Households more Owning Land",
            hole=0.5
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ============================================================
# SUMMARY TABLE
# ============================================================

st.subheader("Species Summary")

summary_display = species_data.copy()

summary_display["Survival Rate"] = (
    summary_display["Surviving"] /
    summary_display["Planted"].replace(0, pd.NA)
) * 100

summary_display["Survival Rate"] = (
    summary_display["Survival Rate"]
    .fillna(0)
    .round(1)
)

st.dataframe(
    summary_display,
    use_container_width=True,
    hide_index=True
)




# ============================================================
# DOWNLOAD
# ============================================================

csv = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_tree_dashboard_data.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Tree Program Monitoring Dashboard | "
    "Built by Wycliff."
)
