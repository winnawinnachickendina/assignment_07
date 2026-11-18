"""
3_Analysis.py — Part 3: where are we high or low, and what are we missing?

Two tabs. Prices: how many prices are below and above the market, then our price
next to every rival's for each item and size, with where we stand — filtered to
the products the owner picks. Gaps: what the rivals sell that we don't
(most-sold first), and what only we sell.

Items the owner has not reviewed yet are left out, with a warning that says so.

Test it: pytest tests/test_pipeline.py -k analysis_page
"""

import os

import pandas as pd
import streamlit as st

from rivals import (
    ABOVE_ALL,
    ABOVE_AVERAGE,
    BELOW_ALL,
    BELOW_AVERAGE,
    DECISIONS_FILE,
    MENUS_FILE,
    add_canonical,
    compare_prices,
    gap_analysis,
    match_items,
    price_table,
)
from rivals.settings import DECISION_COLUMNS

st.set_page_config(layout="wide")
st.title("Salt City: Prices and Gaps")

if not os.path.exists(MENUS_FILE):
    st.info("No menus yet — scrape them on the Scrape page first.")
    st.stop()

menus = pd.read_csv(MENUS_FILE)
if os.path.exists(DECISIONS_FILE):
    decisions = pd.read_csv(DECISIONS_FILE)
else:
    decisions = pd.DataFrame(columns=DECISION_COLUMNS)
matches = match_items(menus, decisions)
waiting = int((matches["status"] == "unreviewed").sum())
if waiting:
    st.warning(
        f"{waiting} rival items still need review and are left out of the analysis. "
        "Finish them on the Review Matches page."
    )

menus = add_canonical(menus, matches)
prices = price_table(menus)
comparison = compare_prices(prices)
gaps = gap_analysis(menus)
prices_tab, gaps_tab = st.tabs(["Prices", "Gaps"])

with prices_tab:
    below = comparison["our_position"].isin([BELOW_ALL, BELOW_AVERAGE])
    above = comparison["our_position"].isin([ABOVE_ALL, ABOVE_AVERAGE])
    below_column, above_column = st.columns(2)
    below_column.metric("Priced below the market", int(below.sum()))
    above_column.metric("Priced above the market", int(above.sum()))

    products = st.multiselect(
        "Products",
        sorted(comparison["canonical"].unique()),
        key="products",
        placeholder="All products",
    )
    shown = (
        comparison[comparison["canonical"].isin(products)] if products else comparison
    )
    st.dataframe(shown, hide_index=True)
    st.caption(
        "👍👍 lower than all of them · 👍 lower than their average · 👉👈 average · "
        "👎 higher than their average · 👎👎 higher than all of them"
    )

with gaps_tab:
    st.subheader("Only them — what we don't sell yet")
    st.dataframe(gaps[gaps["where"] == "only them"], hide_index=True)
    st.subheader("Only us — what sets us apart")
    st.dataframe(gaps[gaps["where"] == "only us"], hide_index=True)

# --- The page: the algorithm, step by step ------------------------------------------
#
# Write the code for each step below its comment. The tests
# (pytest tests/test_pipeline.py -k analysis_page) check the title, the metrics,
# the tab labels, the warning, the product filter, and the tables.
#
# 1. HEADING AND DATA
#    st.set_page_config(layout="wide") — first, so the price table has room for
#    a column per café
#    st.title: Salt City: Prices and Gaps
#    If MENUS_FILE does not exist: st.info(...) and st.stop().
#    menus, decisions and matches exactly as on the Review Matches page.
#    waiting <- how many matches are "unreviewed". If any: st.warning that says how
#    many, that they are left out, and to finish them on the Review Matches page.
#
# 2. THE ANALYSIS (all of it is in the package — the page only calls it)
#    menus <- add_canonical(menus, matches)
#    prices <- price_table(menus)
#    comparison <- compare_prices(prices)
#    gaps <- gap_analysis(menus)
#
# 3. TWO TABS: st.tabs(["Prices", "Gaps"])
#
# 4. THE PRICES TAB (inside `with prices_tab:`)
#    a. Two metrics side by side: "Priced below the market" (rows of comparison
#       whose our_position is BELOW_ALL or BELOW_AVERAGE — .isin([...])) and "Priced
#       above the market" (ABOVE_ALL or ABOVE_AVERAGE). Use the names from rivals,
#       not the text: the labels start with emoji.
#    b. products <- st.multiselect("Products", the sorted unique canonical names
#       in comparison, key="products", placeholder="All products")
#    c. shown <- the rows of comparison whose canonical is in products — or all of
#       comparison when nothing is picked (an empty multiselect means "all").
#       st.dataframe(shown, hide_index=True)
#    d. st.caption that explains the our_position column, e.g. "👍👍 lower than all of
#       them · 👍 lower than their average · 👉👈 average · 👎 higher than their
#       average · 👎👎 higher than all of them".
#
# 5. THE GAPS TAB (inside `with gaps_tab:`)
#    st.subheader "Only them — what we don't sell yet" and st.dataframe of the
#    gaps rows where `where` is "only them"; then st.subheader "Only us — what sets
#    us apart" and the "only us" rows.
