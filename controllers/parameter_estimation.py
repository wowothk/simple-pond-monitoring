from cProfile import label
import streamlit as st
from streamlit_echarts import st_echarts
from lib.parameter_estimation import Estimate
from lib.biomass_after_estimate import single_wt
from lib.plot import Line, LineScatter
import pandas as pd
import numpy as np
import math

def base_section():
    
    st.set_page_config(layout="wide")
    
    t0 = st.sidebar.number_input("t0", value=0)
    sr = st.sidebar.number_input("survival rate", value=0.92)
    n0 = st.sidebar.number_input("n0", value=100)
    T = st.sidebar.number_input("T", value=120)
        
    area = st.sidebar.number_input("area", value=1000)
    # alpha = st.sidebar.number_input("alpha (shrimp growth rate)", value=1.0, step=1.,format="%.2f")/100 

    w0 = st.sidebar.number_input("w0", value=0.05)
    wn = st.sidebar.number_input("wn", value=45)

    partial1 = st.sidebar.number_input("partial1", value=0.1)
    partial2 = st.sidebar.number_input("partial2", value=0.1)
    partial3 = st.sidebar.number_input("partial3", value=0.1)
    
    docpartial1 = int(st.sidebar.number_input("doc partial 1", value=60))
    docpartial2 = int(st.sidebar.number_input("doc partial 2", value=70))
    docpartial3 = int(st.sidebar.number_input("doc partial 3", value=80))
    docfinal = int(st.sidebar.number_input("doc final", value=120))

    # condition = st.sidebar.expander("Conditional Configuration")

    st.sidebar.markdown("## Upload Data")
    df = st.sidebar.file_uploader("Growth Shrimp Data")
    with open("data/growth_full.csv") as f:
        st.sidebar.download_button('See the example of growth shrimp data', f, file_name='growth.csv')


    # e = st.sidebar.number_input("energy day cost", value=4.0, step=1.,format="%.2f")
    # p = st.sidebar.number_input("daily probiotics", value=120000)
    # o = st.sidebar.number_input("others cost", value=30000)
    # labor = st.sidebar.number_input("labor cost", value=2000000)/30
    # bonus = st.sidebar.number_input("bonus", value=2000)
    # h = st.sidebar.number_input("harvest cost per kg", value=1000)
    # r = st.sidebar.number_input("feeding rate", value=0.04)
    # fc = st.sidebar.number_input("feeding price", value=16000)
    # formula = st.sidebar.selectbox("formula", (1, 2))

    submit = st.sidebar.button("submit")

    if submit:
        df = pd.read_csv("data/growth_full.csv", sep=",")
        alpha, alpha2, alpha3, alpha4, alpha5, alpha6 = Estimate(t0, w0, wn, n0, sr, 
                                                    [partial1, partial2, partial3], 
                                                    [docpartial1, docpartial2, docpartial3],
                                                    df["DOC"].tolist(), df["ABW"].tolist(), docfinal).fitting()


        col1, col2 = st.columns(2)

        with col1:
            st.markdown("## Parameter")
            st.latex(
                r"""
                \alpha = {}
                """.format(alpha)
            )

            st.latex(
                r"""\alpha_2 = {}""".format(alpha2)
            )

            st.latex(
                r"""\alpha_3 = {}""".format(alpha3)
            )
            st.latex(
                r"""\alpha_4 = {}""".format(alpha4)
            )
            st.latex(
                r"""\alpha_5 = {}""".format(alpha5)
            )
            st.latex(
                r"""\alpha_6 ={}""".format(alpha6)
            )
        
        with col2:
            st.dataframe(df)

        m = -np.log(sr)/T

        weight = []
        bio = []
        index = list(range(T+1))
        abw = []
        temp = []
        do = []
        nh4 = []
        for t in index:
            wt, biomass = single_wt(t, sr, m, alpha, alpha2, alpha3, alpha4, alpha5, alpha6, 
                t0=t0, wn=wn, w0=w0, n0=n0, ph=[partial1, partial2, partial3], 
                doc=[docpartial1, docpartial2, docpartial3], final_doc=docfinal)
           
            weight.append(wt)
            bio.append(biomass)
            try:
                abw.append(float(df[df["DOC"]== t]["ABW"].values[0]))
                temporary_temp = float(df[df["DOC"]== t]["Temp"].values[0])
                temporary_do = float(df[df["DOC"]== t]["DO"].values[0])
                temporary_nh4 = float(df[df["DOC"]== t]["NH4"].values[0])

                if math.isnan(temporary_temp):
                    temp.append(None)
                else:
                    temp.append(temporary_temp)

                if math.isnan(temporary_do):
                    do.append(None)
                else:
                    do.append(temporary_do)
                
                if math.isnan(temporary_nh4):
                    nh4.append(None)
                else:
                    nh4.append(temporary_nh4)
            except:
                abw.append(None)
                temp.append(None)
                do.append(None)
                nh4.append(None)
    
        option2 = LineScatter("Weight (Gr)", index, weight, index, abw, labels=["estimation", "abw"]).plot()

        st_echarts(options=option2)

        option3 = Line("Temperature", index, y=[temp], labels=["Temperature"]).plot()
        st_echarts(options=option3)

        option4 = Line("Unionized Amonia", index, y=[nh4], labels=["NH4"]).plot()
        st_echarts(options=option4)

        option5 = Line("Dissolved Oxygen", index, y=[do], labels=["DO"]).plot()
        st_echarts(options=option5)

        


            