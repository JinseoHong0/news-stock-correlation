import os
import pandas as pd
import plotly.graph_objects as go

RESULT = "result"
OUT = "charts"
os.makedirs(OUT, exist_ok=True)

# get data
q1 = pd.read_csv("result/q1_market.csv",sep='\t', header=None,
                 names=["market", "weeks", "corr"])
q2 = pd.read_csv("result/q2_category.csv",sep='\t',  header=None,
                 names=["category", "weeks", "articles", "corr"])
q3p = pd.read_csv("result/q3_positive.csv", sep='\t', header=None,
                  names=["code", "name", "industry", "market", "weeks", "corr"])
q3n = pd.read_csv("result/q3_negative.csv", sep='\t', header=None,
                  names=["code", "name", "industry", "market", "weeks", "corr"])

# [Q1] 시장별(지수) 상관계수 막대
fig1 = go.Figure(go.Bar(
    x=q1["market"], y=q1["corr"],
    text=q1["corr"].round(4), textposition="outside"
))
fig1.update_layout(
    title="Q1. 시장별 뉴스 감성-지수 수익률 상관계수",
    xaxis_title="시장", yaxis_title="상관계수"
)
fig1.write_html("{}/q1_market.html".format(OUT))

# [Q2] 카테고리별 상관계수 막대 (양/음 색 구분)
q2 = q2.sort_values("corr")
colors2 = ["crimson" if c < 0 else "steelblue" for c in q2["corr"]]
fig2 = go.Figure(go.Bar(
    x=q2["category"], y=q2["corr"],
    marker_color=colors2,
    text=q2["corr"].round(4), textposition="outside"
))
fig2.update_layout(
    title="Q2. 카테고리별 뉴스 감성-수익률 상관계수",
    xaxis_title="카테고리", yaxis_title="상관계수"
)
fig2.write_html("{}/q2_category.html".format(OUT))

# [Q3-A] 동조 종목 Top 20 (양의 상관)

q3p = q3p.sort_values("corr", ascending=True)
fig3a = go.Figure(go.Bar(
    x=q3p["corr"], y=q3p["name"], orientation="h",
    marker_color="steelblue",
    text=q3p["corr"].round(3), textposition="outside"
))

fig3a.update_layout(
    title="Q3-A. 뉴스 감성과 동조하는 종목 Top 20 (양의 상관)",
    xaxis_title="상관계수", yaxis_title="종목",
    height=600
)
fig3a.write_html("{}/q3_positive.html".format(OUT))

# [Q3-B] 역행 종목 Top 20 (음의 상관)
q3n = q3n.sort_values("corr", ascending=False)
fig3b = go.Figure(go.Bar(
    x=q3n["corr"], y=q3n["name"], orientation="h",
    marker_color="crimson",
    text=q3n["corr"].round(3), textposition="outside"
))

fig3b.update_layout(
    title="Q3-B. 뉴스 감성과 역행하는 종목 Top 20 (음의 상관)",
    xaxis_title="상관계수", yaxis_title="종목",
    height=600
)
fig3b.write_html("{}/q3_negative.html".format(OUT))

# [Q3-C] Top 20 시장 분포 (KOSPI vs KOSDAQ)
pos_dist = q3p["market"].value_counts()
neg_dist = q3n["market"].value_counts()
markets = ["KOSPI", "KOSDAQ"]

fig3c = go.Figure()
fig3c.add_trace(go.Bar(
    name="동조", x=markets,
    y=[int(pos_dist.get(m, 0)) for m in markets],
    text=[int(pos_dist.get(m, 0)) for m in markets], textposition="outside"
))

fig3c.add_trace(go.Bar(
    name="역행", x=markets,
    y=[int(neg_dist.get(m, 0)) for m in markets],
    text=[int(neg_dist.get(m, 0)) for m in markets], textposition="outside"
))
fig3c.update_layout(
    title="Q3-C. 민감 종목 Top 20의 시장 분포 (KOSPI vs KOSDAQ)",
    xaxis_title="시장", yaxis_title="종목 수", barmode="group"
)
fig3c.write_html("{}/q3_market_dist.html".format(OUT))
