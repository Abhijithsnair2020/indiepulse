import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title='IndiePulse | Market Intelligence', page_icon='🎮', layout='wide')
DATA=Path(__file__).parent

st.markdown("""
<style>
:root { --bg:#0b1020; --panel:#111827; --border:#262936; --accent:#8b5cf6; --accent2:#6366f1; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #171a36 0%, #0b1020 44%, #0b1020 100%); }
[data-testid="stMetric"] { background:linear-gradient(180deg,#151b2b,#101522); border:1px solid #262936; border-radius:14px; padding:16px 18px 14px; position:relative; overflow:hidden; }
[data-testid="stMetric"]:before { content:""; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,#8b5cf6,#6366f1,#22d3ee); }
[data-testid="stMetricLabel"] p { color:#aab4c8 !important; font-size:0.88rem !important; }
[data-testid="stMetricValue"] { color:#f4f6ff !important; }
.hero { border:1px solid #282d43; border-radius:20px; padding:28px 30px; margin:4px 0 22px; background:linear-gradient(115deg,rgba(99,102,241,.20),rgba(139,92,246,.09) 45%,rgba(17,24,39,.65)); }
.hero-badge { display:inline-block; color:#c4b5fd; background:rgba(139,92,246,.16); border:1px solid rgba(167,139,250,.30); border-radius:999px; padding:5px 11px; font-size:11px; font-weight:750; letter-spacing:1.1px; }
.hero h1 { margin:12px 0 7px; font-size:2.25rem; color:#f5f6ff; letter-spacing:-1px; }
.hero p { color:#aeb9d0; margin:0; font-size:1rem; }
.insight { border:1px solid #262936; background:rgba(17,24,39,.72); border-radius:13px; padding:14px 16px; min-height:118px; }
.insight-title { color:#aab4c8; font-size:.82rem; margin-bottom:6px; }
.insight-value { color:#e5e7eb; font-weight:700; font-size:1.12rem; }
.insight-note { color:#8491aa; font-size:.8rem; margin-top:5px; }
div[data-testid="stTabs"] button { font-weight:600; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    games=pd.read_csv(DATA/'games.csv',low_memory=False)
    reviews=pd.read_csv(DATA/'review_summary.csv')
    games=games.merge(reviews,on='appid',how='left')
    games['sample_review_count']=games['sample_review_count'].fillna(0)
    games['sample_positive_pct']=games['sample_positive_pct'].fillna(0)
    games['price_usd_est']=pd.to_numeric(games['mat_final_price'],errors='coerce')/100
    games.loc[games['mat_currency'].fillna('')!='USD','price_usd_est']=np.nan
    games['release_date']=pd.to_datetime(games['release_date'],errors='coerce')
    games['genre_list']=games['genres'].fillna('').apply(lambda x:[g.strip() for g in x.split(';') if g.strip()])
    return games

df=load_data()
# A transparent heuristic for identifying indie-labeled games in this multilingual dataset.
indie_terms=['indie','nezávislé','インディー','independent','indie game','indie games','indie giochi','indie oyun']
def indie_flag(gs):
    return any(any(term in g.lower() for term in indie_terms) for g in gs)
df['indie_label']=df.genre_list.apply(indie_flag)

st.markdown("""
<div class="hero">
  <span class="hero-badge">STEAM INDIE MARKET INTELLIGENCE</span>
  <h1>🎮 IndiePulse</h1>
  <p>Explore indie-game niches, compare market signals, and turn a dataset into better questions.</p>
</div>
""", unsafe_allow_html=True)
st.caption('Steam Store snapshot (January 2025) · Experimental indicators, not forecasts')

# Search & benchmark a specific game (global catalog, independent of niche filters)
st.markdown("### 🔍 Search & Benchmark a Specific Game")
st.caption("Look up a game in the catalog and compare its listed USD price with the dataset median.")
search_names=df['name'].dropna().astype(str).sort_values().unique().tolist()
benchmark_choice=st.selectbox("Search for a game", options=["— Select a game —"]+search_names, index=0, placeholder="Type a game name...")
if benchmark_choice != "— Select a game —":
    game_rows=df[df['name'].astype(str)==benchmark_choice]
    game=game_rows.iloc[0]
    overall_median_price=df['price_usd_est'].dropna().median() if df['price_usd_est'].notna().any() else np.nan
    game_price=game['price_usd_est']
    if pd.notna(game_price) and pd.notna(overall_median_price):
        price_comparison=f"${game_price:.2f} vs ${overall_median_price:.2f}"
        price_note="Game price vs overall dataset median (USD)"
    else:
        price_comparison="N/A"
        price_note="USD comparison unavailable for this game"
    reviews_value=int(game['sample_review_count']) if pd.notna(game['sample_review_count']) else 0
    positive_value=float(game['sample_positive_pct']) if pd.notna(game['sample_positive_pct']) else 0.0
    tags_value=str(game['genres']) if pd.notna(game['genres']) and str(game['genres']).strip() else "No genre/tag data available"
    b1,b2,b3=st.columns(3)
    with b1:
        st.markdown(f'<div class="insight"><div class="insight-title">Price benchmark</div><div class="insight-value">{price_comparison}</div><div class="insight-note">{price_note}</div></div>',unsafe_allow_html=True)
    with b2:
        st.markdown(f'<div class="insight"><div class="insight-title">Reviews & positive share</div><div class="insight-value">{reviews_value:,} reviews · {positive_value:.1f}% positive</div><div class="insight-note">Review sample represented in this dataset</div></div>',unsafe_allow_html=True)
    with b3:
        st.markdown(f'<div class="insight"><div class="insight-title">Genres / tags</div><div class="insight-value">{tags_value}</div><div class="insight-note">Dataset genre labels</div></div>',unsafe_allow_html=True)


with st.sidebar:
    st.header('🔎 Explore')
    use_indie=st.checkbox('Restrict to games with a detected Indie genre label',value=True)
    min_reviews=st.slider('Minimum reviews in dataset sample',25,1000,25,step=25)
    price_cap=st.slider('Maximum price (USD; only rows with USD price)',0.0,100.0,30.0,step=1.0)
    st.caption('Prices are only comparable for rows marked USD. Dataset genres are multilingual and the Indie filter is imperfect.')
base=df.copy()
if use_indie: base=base[base.indie_label]
base=base[(base.sample_review_count>=min_reviews)&(base.price_usd_est.fillna(0)<=price_cap)]
all_genres=sorted(set(g for gs in base.genre_list for g in gs if g))
selected=st.multiselect('Choose up to 3 genres / tags to explore',all_genres,max_selections=3,placeholder='Choose genres')
if selected:
    subset=base[base.genre_list.apply(lambda gs:all(g in gs for g in selected))]
else:
    subset=base.copy()

n=len(subset)
median_rating=subset.sample_positive_pct.median() if n else 0
median_price=subset.price_usd_est.dropna().median() if n and subset.price_usd_est.notna().any() else 0
median_reviews=subset.sample_review_count.median() if n else 0
subset=subset.copy()
subset['estimated_gross_usd']=subset.sample_review_count*subset.price_usd_est*35

# Existing metric calculations retained; display and navigation are polished.
tab_overview,tab_pricing,tab_games,tab_method=st.tabs(['📊 Market Overview','💰 Pricing & Revenue','🎮 Games in Niche','📘 Methodology'])
with tab_overview:
    cols=st.columns(4)
    cols[0].metric('Games in selected niche',f'{n:,}')
    cols[1].metric('Median positive-review %',f'{median_rating:.1f}%')
    cols[2].metric('Median price (USD)',f'${median_price:.2f}' if median_price else 'N/A')
    cols[3].metric('Median review count',f'{median_reviews:,.0f}')
    st.markdown('### Quick Insight')
    q1,q2,q3=st.columns(3)
    q1.markdown(f'<div class="insight"><div class="insight-title">Niche size</div><div class="insight-value">{n:,} games</div><div class="insight-note">Matches current filters</div></div>',unsafe_allow_html=True)
    q2.markdown(f'<div class="insight"><div class="insight-title">Review signal</div><div class="insight-value">{median_rating:.1f}% positive</div><div class="insight-note">Median in this dataset sample</div></div>',unsafe_allow_html=True)
    q3.markdown(f'<div class="insight"><div class="insight-title">Typical listed price</div><div class="insight-value">{("$"+format(median_price,".2f")) if median_price else "N/A"}</div><div class="insight-note">Median USD price, where available</div></div>',unsafe_allow_html=True)
    st.markdown('### Niche overview')
    if not n:
        st.info('No games match these filters. Try clearing genre selection or adjusting the review threshold.')
    else:
        niche_competition=max(n,1)
        quality=np.clip(median_rating/100,0,1)
        activity=np.clip(np.log1p(median_reviews)/np.log1p(max(base.sample_review_count.max(),1)),0,1)
        scarcity=np.clip(1-np.log1p(niche_competition)/np.log1p(max(len(base),2)),0,1)
        score=int(round(100*(0.5*quality+0.25*activity+0.25*scarcity)))
        st.metric('Experimental Niche Opportunity Score',score)
        st.caption('Heuristic: 50% median positive-review signal, 25% review activity, 25% relative scarcity. It is not validated and scarcity alone can indicate low demand.')
        left,right=st.columns(2)
        with left:
            st.markdown('**Games by selected genre(s)**')
            genre_counts=pd.Series([g for gs in subset.genre_list for g in gs]).value_counts().head(20)
            st.bar_chart(genre_counts)
        with right:
            st.markdown('**Price tiers: average review activity**')
            price=subset.dropna(subset=['price_usd_est']).copy()
            price=price[price.price_usd_est>=0]
            bins=[-0.01,5,10,15,20,30,50,1000]
            labels=['Free/≤$5','$5–10','$10–15','$15–20','$20–30','$30–50','$50+']
            price['tier']=pd.cut(price.price_usd_est,bins=bins,labels=labels)
            chart=price.groupby('tier',observed=False).agg(avg_reviews=('sample_review_count','mean'),games=('appid','count')).reset_index()
            chart=chart[chart.games>0]
            if len(chart): st.bar_chart(chart.set_index('tier')[['avg_reviews']])
            else: st.info('Not enough comparable USD-priced games for this chart.')
with tab_pricing:
    st.markdown('### Price tiers and illustrative gross estimates')
    if n:
        price=subset.dropna(subset=['price_usd_est']).copy()
        price=price[price.price_usd_est>=0]
        bins=[-0.01,5,10,15,20,30,50,1000]
        labels=['Free/≤$5','$5–10','$10–15','$15–20','$20–30','$30–50','$50+']
        price['tier']=pd.cut(price.price_usd_est,bins=bins,labels=labels)
        chart=price.groupby('tier',observed=False).agg(avg_reviews=('sample_review_count','mean'),avg_gross=('estimated_gross_usd','mean'),games=('appid','count')).reset_index()
        chart=chart[chart.games>0]
        if len(chart):
            st.markdown('**Average review count by price tier**')
            st.bar_chart(chart.set_index('tier')[['avg_reviews']])
            st.markdown('**Illustrative gross estimate by tier (USD)**')
            st.bar_chart(chart.set_index('tier')[['avg_gross']])
            st.dataframe(chart,hide_index=True,use_container_width=True)
    else: st.info('No games match the current filters.')
    st.caption('Illustrative estimate = reviews in sample × USD price × 35. This is not actual revenue.')
with tab_games:
    st.markdown('### Selected games')
    if not n:
        st.info('No games match these filters.')
    else:
        display=subset.sort_values('sample_review_count',ascending=False)[['appid','name','release_date','genres','mat_currency','mat_final_price','price_usd_est','sample_review_count','sample_positive_pct','estimated_gross_usd']].copy()
        display['release_date']=display.release_date.dt.strftime('%Y-%m-%d')
        display=display.rename(columns={'appid':'Steam ID','name':'Game','release_date':'Release','genres':'Genres','mat_currency':'Currency','mat_final_price':'Dataset price','price_usd_est':'USD price (approx.)','sample_review_count':'Reviews in sample','sample_positive_pct':'Positive reviews (%)','estimated_gross_usd':'Illustrative gross estimate (USD)'})
        st.dataframe(display,hide_index=True,use_container_width=True)
        st.download_button('⬇️ Download filtered games CSV',display.to_csv(index=False).encode('utf-8'),file_name='indiepulse_filtered.csv',mime='text/csv')
with tab_method:
    st.markdown('### Methodology & limitations')
    st.markdown('''- **Dataset:** Steam Store catalog snapshot from January 2025, packaged in the uploaded Kaggle dataset. This is not live data.
- **Genre selection:** Genre labels are multilingual. The detected Indie filter searches a small set of Indie translations and may miss or misclassify games.
- **Reviews:** Counts and positive share are calculated from the review rows included in this dataset, not necessarily all Steam reviews or a current review score.
- **Price:** Only rows with USD currency are used for USD comparisons. Prices are converted from the dataset's integer minor-unit format (÷100), an assumption that should be checked against source documentation.
- **Estimated gross:** reviews × price × 35 is a rough illustrative Boxleiter-style multiplier. It is not actual revenue, ignores discounts, refunds, regional pricing, review bias and other factors, and should not be used for financial decisions.
- **Opportunity score:** an experimental heuristic, not a predictive model. Low competition may simply mean low demand.
''')
    st.caption('IndiePulse is an exploratory research project. Use these signals to ask better questions, not to make guaranteed business decisions.')

st.markdown('---')
st.markdown('<div style="text-align:center;color:#7d8aa5;font-size:.85rem">IndiePulse · Independent indie-market exploration · <a href="mailto:feedback@example.com" style="color:#a78bfa">Feedback (placeholder)</a></div>',unsafe_allow_html=True)

st.markdown("---")
st.markdown("💬 **Building an indie game?** [Rate IndiePulse & request a feature (30 sec)](https://docs.google.com/forms/d/e/1FAIpQLSd7_bUu5qeYNM2z51XiqQgmIlUs0ANmWGWS1SRvY6yzhiwFYQ/viewform?usp=dialog)")
