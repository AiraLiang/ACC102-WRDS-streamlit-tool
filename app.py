import wrds
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ======================
# 全局配置
# ======================
plt.style.use('seaborn-v0_8-whitegrid')
st.set_page_config(page_title="Financial Analysis Tool", layout="wide")

# ======================
# 核心数据获取与计算函数
# ======================
def analyze_company(tic, wrds_username, wrds_password, start_year, end_year):
    """
    从WRDS获取财务数据并计算指标
    """
    try:
        db = wrds.Connection(wrds_username=wrds_username, wrds_password=wrds_password)
        
        sql = f"""
        SELECT
            gvkey, conm, tic, fyear,
            revt, cogs, ni, at, ceq, dlc, dltt, ebitda, xint
        FROM comp.funda
        WHERE 
            tic = '{tic}'
            AND fyear BETWEEN {start_year} AND {end_year}
            AND indfmt='INDL' AND datafmt='STD'
            AND popsrc='D' AND consol='C'
        ORDER BY fyear;
        """
        
        df_raw = db.raw_sql(sql)
        db.close()

        if df_raw.empty:
            return None, None

        # 计算各项财务指标
        df_raw['Gross Margin'] = (df_raw['revt'] - df_raw['cogs']) / df_raw['revt']
        df_raw['Net Profit Margin'] = df_raw['ni'] / df_raw['revt']
        df_raw['ROE'] = df_raw['ni'] / df_raw['ceq']
        df_raw['ROA'] = df_raw['ni'] / df_raw['at']
        df_raw['EBITDA Margin'] = df_raw['ebitda'] / df_raw['revt']
        
        # 计算ICR并处理异常值
        df_raw['ICR'] = df_raw['ebitda'] / df_raw['xint']
        df_raw['ICR'] = df_raw['ICR'].replace([np.inf, -np.inf], np.nan)
        df_raw['ICR'] = df_raw['ICR'].fillna(999)

        company_name = df_raw['conm'].iloc[0]
        return df_raw, company_name
    except Exception as e:
        st.error(f"WRDS Connection Failed: {str(e)}")
        st.info("Please check your username and password.")
        return None, None

# ======================
# 财务健康度评分（彩色条样式）
# ======================
def financial_health_summary(df, latest_year, company_label):
    """
    彩色条健康评分样式
    """
    latest = df[df['fyear'] == latest_year].iloc[0]
    
    st.subheader(f"✅ Financial Health Summary — {company_label}")

    # 1. Profitability (Gross Margin)
    gm = latest['Gross Margin']
    if gm > 0.4:
        st.success("Profitability: Strong (Gross Margin > 40%)")
    elif gm > 0.2:
        st.info("Profitability: Medium (20% ≤ Gross Margin ≤ 40%)")
    else:
        st.warning("Profitability: Weak (Gross Margin < 20%)")

    # 2. EBITDA Margin
    em = latest['EBITDA Margin']
    if em > 0.2:
        st.success("EBITDA Margin: Strong (>20%)")
    elif em > 0.1:
        st.info("EBITDA Margin: Medium (10% - 20%)")
    else:
        st.warning("EBITDA Margin: Low (<10%)")

    # 3. ICR
    icr = latest['ICR']
    if icr == 999:
        st.info("ICR: Not Applicable (No Interest Expense / Debt)")
    elif icr > 5:
        st.success("ICR: Very Safe (Covers Interest >5x)")
    elif icr > 2:
        st.info("ICR: Moderate (2-5x)")
    else:
        st.warning("ICR: Risky (<2x)")

    # 4. Growth (ROE Trend)
    roe_trend = (df['ROE'].iloc[-1] - df['ROE'].iloc[0]) / df['ROE'].iloc[0]
    if roe_trend > 0.1:
        st.success("Growth: Improving (ROE up >10%)")
    elif abs(roe_trend) <= 0.1:
        st.info("Growth: Stable (ROE ±10%)")
    else:
        st.warning("Growth: Declining (ROE down >10%)")

    # 5. Asset Efficiency (ROA)
    roa = latest['ROA']
    if roa > 0.1:
        st.success("Asset Efficiency: Strong (ROA > 10%)")
    elif roa > 0.05:
        st.info("Asset Efficiency: Medium (5%-10%)")
    else:
        st.warning("Asset Efficiency: Weak (<5%)")

# ======================
# 主界面
# ======================
def main():
    st.title("📊 WRDS Financial Analysis Tool")
    st.markdown("---")

    # 1. WRDS 登录
    st.subheader("🔐 WRDS Account Login")
    wrds_user = st.text_input("WRDS Username:", placeholder="e.g. john123")
    wrds_pwd = st.text_input("WRDS Password:", type="password", placeholder="Your WRDS password")

    st.markdown("---")

    # 2. 年份选择
    st.subheader("📅 Select Analysis Period")
    if "sy" not in st.session_state:
        st.session_state.sy = 2020
    if "ey" not in st.session_state:
        st.session_state.ey = 2024

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("Last 5 Years"):
            st.session_state.sy = 2020
            st.session_state.ey = 2024
    with col_b:
        if st.button("Last 10 Years"):
            st.session_state.sy = 2015
            st.session_state.ey = 2024
    with col_c:
        if st.button("Reset 2020-2024"):
            st.session_state.sy = 2020
            st.session_state.ey = 2024

    col1, col2 = st.columns(2)
    with col1:
        start_year = st.number_input("Start Year", min_value=2000, max_value=2024, key="sy")
    with col2:
        end_year = st.number_input("End Year", min_value=2000, max_value=2024, key="ey")

    if start_year > end_year:
        st.error("Start Year cannot be later than End Year!")
        return

    st.markdown("---")

    # 3. 图表类型选择
    st.subheader("📊 Chart Type")
    chart_type = st.radio("Choose style", ["Line Plot", "Bar Chart"], horizontal=True)

    # 4. 指标选择
    st.subheader("📈 Select Indicators to Display")
    indicators = [
        "Gross Margin",
        "Net Profit Margin",
        "ROE",
        "ROA",
        "EBITDA Margin",
        "ICR"
    ]
    selected = st.multiselect("Choose which indicators to plot:", indicators, default=indicators)

    st.markdown("---")

    # 5. 公司输入
    st.subheader("🏢 Company(s)")
    tic1 = st.text_input("Ticker 1 (Main)", "KO").strip().upper()
    enable_compare = st.checkbox("Enable Company Comparison (vs Ticker 2)")
    tic2 = st.text_input("Ticker 2 (Compare)", "PEP").strip().upper() if enable_compare else None

    # 执行分析
    if st.button("🚀 Run Analysis", type="primary"):
        if not wrds_user or not wrds_pwd:
            st.error("Please enter your WRDS username and password first!")
            return

        # 获取主公司数据
        df1, name1 = analyze_company(tic1, wrds_user, wrds_pwd, start_year, end_year)
        if df1 is None:
            st.error(f"❌ No data found for {tic1}. Please check the ticker symbol.")
            return

        latest_year = df1['fyear'].max()

        # 获取对比公司数据
        df2, name2 = None, None
        if enable_compare and tic2:
            df2, name2 = analyze_company(tic2, wrds_user, wrds_pwd, start_year, end_year)
            if df2 is None:
                st.warning(f"No data available for {tic2}")

        # ==========================================================
        # 上下排列 Key Metrics（先主公司，再对比公司）
        # ==========================================================
        st.subheader(f"📊 Key Metrics ({latest_year})")

        # 1. 主公司
        st.markdown(f"### {name1} ({tic1})")
        latest1 = df1[df1['fyear'] == latest_year].iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Revenue", f"${latest1['revt']:,.0f}M")
        with c2:
            st.metric("Net Income", f"${latest1['ni']:,.0f}M")
        with c3:
            st.metric("ROE", f"{latest1['ROE']*100:.1f}%")
        with c4:
            st.metric("ROA", f"{latest1['ROA']*100:.1f}%")
        with c5:
            icr_val = f"{latest1['ICR']:.1f}x" if latest1['ICR'] != 999 else "N/A"
            st.metric("ICR", icr_val)

        # 2. 对比公司（如果开启）
        if enable_compare and df2 is not None:
            st.markdown("---")
            st.markdown(f"### {name2} ({tic2})")
            latest2 = df2[df2['fyear'] == latest_year].iloc[0]
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.metric("Revenue", f"${latest2['revt']:,.0f}M")
            with d2:
                st.metric("Net Income", f"${latest2['ni']:,.0f}M")
            with d3:
                st.metric("ROE", f"{latest2['ROE']*100:.1f}%")
            with d4:
                st.metric("ROA", f"{latest2['ROA']*100:.1f}%")
            with d5:
                icr_val = f"{latest2['ICR']:.1f}x" if latest2['ICR'] != 999 else "N/A"
                st.metric("ICR", icr_val)

        st.markdown("---")

        # ==========================================================
        # 财务健康总结也上下排列
        # ==========================================================
        if enable_compare and df2 is not None:
            st.subheader("✅ Financial Health Summary Comparison")
            col_left, col_right = st.columns(2)
            with col_left:
                financial_health_summary(df1, latest_year, f"{name1} ({tic1})")
            with col_right:
                financial_health_summary(df2, latest_year, f"{name2} ({tic2})")
            st.markdown("---")
        else:
            financial_health_summary(df1, latest_year, f"{name1} ({tic1})")
            st.markdown("---")

        # 数据下载（主公司）
        csv1 = df1.to_csv(index=False).encode("utf-8")
        st.download_button("Download Main Company Data", csv1, f"{tic1}_data.csv", "text/csv")

        # 对比公司数据下载（新增）
        if enable_compare and df2 is not None:
            csv2 = df2.to_csv(index=False).encode("utf-8")
            st.download_button("Download Compare Company Data", csv2, f"{tic2}_data.csv", "text/csv")

        st.markdown("---")

        # ==========================================================
        # 数据表格：先主公司，再对比公司（上下排列）
        # ==========================================================
        # 1. 主公司表格
        st.subheader(f"📋 {name1} ({tic1}) - {start_year}-{end_year} Financial Data")
        show_cols = ['fyear', 'revt', 'ni', 'Gross Margin', 'Net Profit Margin', 'ROE', 'ROA', 'EBITDA Margin', 'ICR']
        st.dataframe(df1[show_cols].round(4), use_container_width=True)

        # 2. 对比公司表格（新增，放在主公司表格下面）
        if enable_compare and df2 is not None:
            st.markdown("---")
            st.subheader(f"📋 {name2} ({tic2}) - {start_year}-{end_year} Financial Data")
            st.dataframe(df2[show_cols].round(4), use_container_width=True)

        st.markdown("---")

        # 绘图
        if not selected:
            st.info("Please select at least one indicator to display charts.")
            return

        if enable_compare and df2 is not None:
            plot_title = f"Financial Ratios Trend: {name1} vs {name2} ({start_year}-{end_year})"
        else:
            plot_title = f"Financial Ratios Trend: {name1} ({start_year}-{end_year})"

        st.subheader("📈 Selected Financial Ratios Trend")
        n = len(selected)
        rows = (n + 1) // 2
        fig, axes = plt.subplots(rows, 2, figsize=(14, 5 * rows))
        axes = axes.flatten()
        idx = 0

        years = df1['fyear']
        bar_width = 0.35

        for ind in selected:
            ax = axes[idx]
            y1 = df1[ind].copy()
            if ind in ["Gross Margin","Net Profit Margin","ROE","ROA","EBITDA Margin"]:
                y1 = y1 * 100
            if ind == "ICR":
                y1 = y1.replace(999, np.nan)
                if chart_type == "Bar Chart":
                    y1 = y1.fillna(0)

            if chart_type == "Line Plot":
                ax.plot(years, y1, marker='o', label=tic1, linewidth=2.5)
            else:
                ax.bar(years - bar_width/2, y1, width=bar_width, alpha=0.7, label=tic1)

            if enable_compare and df2 is not None:
                y2 = df2[ind].copy()
                if ind in ["Gross Margin","Net Profit Margin","ROE","ROA","EBITDA Margin"]:
                    y2 = y2 * 100
                if ind == "ICR":
                    y2 = y2.replace(999, np.nan)
                    if chart_type == "Bar Chart":
                        y2 = y2.fillna(0)

                if chart_type == "Line Plot":
                    ax.plot(years, y2, marker='s', label=tic2, linestyle='--')
                else:
                    ax.bar(years + bar_width/2, y2, width=bar_width, alpha=0.7, label=tic2)

            ax.set_title(ind, fontsize=12)
            ax.legend()
            ax.grid(alpha=0.3)
            idx += 1

        for i in range(idx, len(axes)):
            axes[i].axis('off')

        plt.suptitle(plot_title, fontsize=16)
        plt.tight_layout()
        st.pyplot(fig)

if __name__ == "__main__":
    main()