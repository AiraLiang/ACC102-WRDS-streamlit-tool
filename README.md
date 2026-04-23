# WRDS Financial Analysis Tool
## ACC102 Mini Assignment - Track 4 (Interactive Data Analysis Tool)

An interactive financial analysis web application built with **Streamlit** that retrieves annual corporate data from **WRDS `Compustat`**, automatically computes key financial ratios, and supports dual‑company comparison with visualisation and financial health evaluation.

---

## 1. Problem & User
This tool addresses the need for quick, visual analysis of corporate financial performance using reliable, standardised data.  
**Target users**: Accounting and finance students, academic researchers, and non‑technical users who need clear insights into profitability, solvency, efficiency, and growth trends without complex coding.

---

## 2. Data
- **Source**: WRDS `Compustat` Fundamentals Annual (`comp.funda`)
- **Access method**: Python SQL query via the `wrds` library
- **Key fields used**: `revt`, `cogs`, `ni`, `at`, `ceq`, `ebitda`, `xint`
- **Time range**: User‑selectable (2000–2024)
- **Filters**: Standard industrial format, consolidated statements

---

## 3. Methods
The analysis follows these core steps using Python and key libraries:
1. Connect to the WRDS database using the `wrds` library
2. Extract financial data for selected companies and years
3. Clean and process missing/infinite values using `pandas` and `numpy`
4. Calculate key financial ratios (profitability, efficiency, solvency)
5. Generate interactive visualisations with `matplotlib` and Streamlit components
6. Support dual‑company comparison and CSV export functionality
---

## 4. Key Findings / Features
- Clear profitability, efficiency, and solvency analysis
- Automatic colour‑coded financial health summary
- Interactive line & bar charts
- Dual‑company comparison mode
- Full data table display
- CSV data export
- Customisable time period selection

---

## 5. How to run locally
1. Install required packages:
```base 
pip install -r requirements.txt
```
2. Launch the application:
```base
streamlit run app.py
```
3. Enter your WRDS username and password
4. Input company tickers (e.g., KO, PEP) and run analysis
---

## 6.  Product Information
### Project files

• `app.py`: Main interactive financial analysis tool

• `requirements.txt`: Dependencies

• `README.md`: Project documentation

### Product link
The application is deployed on Streamlit Cloud:  
`https://acc102-wrds-app-tool-zxcvb.streamlit.app/`

---

## 7. Limitations & Improvements

• Requires a valid WRDS account

• Only annual data is supported

• ICR is unavailable for firms with no interest expense

• Future improvements: quarterly data, industry benchmarks, PDF report export

---

## Academic Integrity

This project is completed for the ACC102 individual assignment. All Python analysis, logic, and interface design are original work. AI tools are used only for documentation and formatting support with full disclosure in the reflection report.
