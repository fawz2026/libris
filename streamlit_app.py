"""
LIBRIS - Advanced Librarian AI Agent
Streamlit Web Interface

A powerful tool for bibliographic research, document processing,
and knowledge curation in philosophy and history.
"""

import streamlit as st
import sys
import os
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import io

# Fix import path for Streamlit Cloud
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Now import LIBRIS modules
from core.libris_agent import LIBRISAgent
from knowledge_base.base_collection import initialize_catalog

# Page configuration
st.set_page_config(
    page_title="LIBRIS - Advanced Librarian AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f4788;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stat-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_agent():
    """Load or initialize LIBRIS agent"""
    kb_path = Path('knowledge_base/libris_catalog.json')
    
    if not kb_path.exists():
        # Initialize with base collection
        catalog = initialize_catalog()
        kb_path.parent.mkdir(parents=True, exist_ok=True)
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    return LIBRISAgent(str(kb_path))


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">🏛️ LIBRIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Advanced Librarian AI Agent for Historical & Philosophical Collections</div>', unsafe_allow_html=True)
    
    # Initialize agent
    agent = load_agent()
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1f4788/ffffff?text=LIBRIS", use_container_width=True)
        
        st.markdown("### About LIBRIS")
        st.markdown("""
        LIBRIS is an intelligent librarian AI that helps you:
        - 📚 Search 74+ curated philosophical works
        - 📄 Process bibliographies from documents
        - 🔍 Find works by theme, period, or author
        - 📤 Export to multiple formats
        
        **Created by**: Claude & Plato  
        **Institution**: Indiana University
        """)
        
        # Statistics
        st.markdown("---")
        st.markdown("### 📊 Catalog Statistics")
        stats = agent.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Works", stats['total_entries'])
            st.metric("Authors", stats['total_authors'])
        with col2:
            st.metric("Themes", stats['total_themes'])
            st.metric("Sources", stats['sources'])
        
        if stats['date_range']:
            st.info(f"**Date Range**: {stats['date_range'][0]} to {stats['date_range'][1]}")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Search", 
        "📄 Process Document", 
        "📊 Explore Collection",
        "📤 Export",
        "ℹ️ About"
    ])
    
    # TAB 1: SEARCH
    with tab1:
        st.header("🔍 Search the Collection")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input(
                "Enter your search query",
                placeholder="e.g., social contract, ethics, Plato, enlightenment...",
                help="Search by keywords, author names, themes, or time periods"
            )
        
        with col2:
            search_type = st.selectbox(
                "Search Mode",
                ["Comprehensive", "Keyword", "Conceptual", "Fuzzy"],
                help="Comprehensive combines all search strategies"
            )
        
        max_results = st.slider("Maximum results", 5, 50, 15)
        
        if st.button("🔍 Search", type="primary"):
            if query:
                with st.spinner("Searching..."):
                    results = agent.search(
                        query, 
                        max_results=max_results,
                        search_type=search_type.lower()
                    )
                
                if results:
                    st.success(f"Found {len(results)} results")
                    
                    # Display results
                    for i, result in enumerate(results, 1):
                        entry = result['entry']
                        score = result.get('score', 0)
                        
                        with st.expander(f"{i}. {entry.get('author', 'Unknown')} ({entry.get('date', 'Unknown')}) - Score: {score:.2f}"):
                            st.markdown(f"**Title**: {entry.get('title', 'Unknown')}")
                            
                            if entry.get('themes'):
                                st.markdown(f"**Themes**: {', '.join(entry['themes'])}")
                            
                            if entry.get('period'):
                                st.markdown(f"**Period**: {entry.get('period')}")
                            
                            if entry.get('notes'):
                                st.markdown(f"**Notes**: {entry.get('notes')}")
                            
                            if result.get('matched_fields'):
                                st.caption(f"Matched in: {', '.join(result['matched_fields'])}")
                    
                    # Export search results
                    st.markdown("---")
                    st.markdown("### Export Search Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📄 Export to CSV"):
                            csv_path = agent.export(results, format='csv')
                            with open(csv_path, 'r', encoding='utf-8') as f:
                                st.download_button(
                                    "Download CSV",
                                    f.read(),
                                    file_name=f"libris_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                    
                    with col2:
                        if st.button("📚 Export to BibTeX"):
                            bibtex_path = agent.export(results, format='bibtex')
                            with open(bibtex_path, 'r', encoding='utf-8') as f:
                                st.download_button(
                                    "Download BibTeX",
                                    f.read(),
                                    file_name=f"libris_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bib",
                                    mime="text/plain"
                                )
                    
                    with col3:
                        if st.button("📝 Export to Markdown"):
                            md_path = agent.export(results, format='markdown')
                            with open(md_path, 'r', encoding='utf-8') as f:
                                st.download_button(
                                    "Download Markdown",
                                    f.read(),
                                    file_name=f"libris_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                    mime="text/markdown"
                                )
                
                else:
                    st.warning("No results found. Try different keywords or search mode.")
            else:
                st.warning("Please enter a search query")
    
    # TAB 2: PROCESS DOCUMENT
    with tab2:
        st.header("📄 Process Document")
        st.markdown("""
        Upload a bibliography, syllabus, or reading list to extract bibliographic data.
        
        **Supported formats**: PDF, DOCX, TXT, CSV, XLSX, TSV, Markdown
        """)
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt', 'csv', 'xlsx', 'tsv', 'md'],
            help="Upload a bibliography, syllabus, or reading list"
        )
        
        if uploaded_file:
            st.info(f"**File**: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            if st.button("🚀 Process Document", type="primary"):
                with st.spinner("Processing document... This may take a moment."):
                    # Save uploaded file temporarily
                    temp_path = Path(f"temp_{uploaded_file.name}")
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    try:
                        # Process document
                        report = agent.process_document(str(temp_path))
                        
                        # Save updated catalog
                        agent.save_catalog()
                        
                        # Display results
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.markdown("### ✅ Document Processed Successfully!")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Entries Added", report['entries_added'])
                        with col2:
                            st.metric("Duplicates Found", report['duplicates_found'])
                        with col3:
                            st.metric("Themes Detected", len(report.get('themes_detected', [])))
                        with col4:
                            st.metric("Quality Issues", len(report.get('quality_issues', [])))
                        
                        if report.get('themes_detected'):
                            st.markdown(f"**Themes**: {', '.join(report['themes_detected'][:10])}")
                        
                        if report.get('date_range'):
                            st.markdown(f"**Date Range**: {report['date_range'][0]} to {report['date_range'][1]}")
                        
                        if report.get('quality_issues'):
                            with st.expander("⚠️ View Quality Issues"):
                                for issue in report['quality_issues'][:20]:
                                    st.caption(f"• {issue}")
                        
                        # Clear cache to reload agent with new data
                        st.cache_resource.clear()
                        
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
                    
                    finally:
                        # Clean up temp file
                        if temp_path.exists():
                            temp_path.unlink()
    
    # TAB 3: EXPLORE COLLECTION
    with tab3:
        st.header("📊 Explore the Collection")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            filter_type = st.selectbox(
                "Browse by",
                ["All Works", "By Author", "By Theme", "By Period", "By Date Range"]
            )
        
        if filter_type == "By Author":
            authors = list(agent.catalog['indices']['by_author'].keys())
            selected_author = st.selectbox("Select Author", sorted(authors))
            
            if selected_author:
                indices = agent.catalog['indices']['by_author'][selected_author]
                entries = [agent.catalog['entries'][i] for i in indices]
                
                st.markdown(f"### Works by {selected_author}")
                for entry in entries:
                    with st.expander(f"{entry.get('date', 'Unknown')} - {entry.get('title', 'Unknown')}"):
                        if entry.get('themes'):
                            st.markdown(f"**Themes**: {', '.join(entry['themes'])}")
                        if entry.get('notes'):
                            st.markdown(f"**Notes**: {entry.get('notes')}")
        
        elif filter_type == "By Theme":
            themes = list(agent.catalog['indices']['by_theme'].keys())
            selected_theme = st.selectbox("Select Theme", sorted(themes))
            
            if selected_theme:
                indices = agent.catalog['indices']['by_theme'][selected_theme]
                entries = [agent.catalog['entries'][i] for i in indices]
                
                st.markdown(f"### Works on {selected_theme}")
                for entry in entries:
                    with st.expander(f"{entry.get('author', 'Unknown')} - {entry.get('title', 'Unknown')}"):
                        st.markdown(f"**Date**: {entry.get('date', 'Unknown')}")
                        if entry.get('notes'):
                            st.markdown(f"**Notes**: {entry.get('notes')}")
        
        elif filter_type == "By Period":
            periods = list(agent.catalog['indices']['by_period'].keys())
            selected_period = st.selectbox("Select Period", sorted(periods))
            
            if selected_period:
                indices = agent.catalog['indices']['by_period'][selected_period]
                entries = [agent.catalog['entries'][i] for i in indices]
                
                st.markdown(f"### Works from {selected_period}")
                for entry in entries:
                    with st.expander(f"{entry.get('author', 'Unknown')} - {entry.get('title', 'Unknown')}"):
                        st.markdown(f"**Date**: {entry.get('date', 'Unknown')}")
                        if entry.get('themes'):
                            st.markdown(f"**Themes**: {', '.join(entry['themes'])}")
        
        else:  # All Works
            st.markdown("### All Works in Catalog")
            
            # Create DataFrame for better display
            df_data = []
            for entry in agent.catalog['entries'][:100]:  # Limit to first 100
                df_data.append({
                    'Date': entry.get('date', 'Unknown'),
                    'Author': entry.get('author', 'Unknown'),
                    'Title': entry.get('title', 'Unknown'),
                    'Period': entry.get('period', 'Unknown')
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, height=600)
    
    # TAB 4: EXPORT
    with tab4:
        st.header("📤 Export Collection")
        
        st.markdown("""
        Export your entire catalog or filtered results in various formats.
        Perfect for citations, bibliographies, or data analysis.
        """)
        
        export_format = st.selectbox(
            "Select Export Format",
            ["CSV (Spreadsheet)", "BibTeX (LaTeX)", "JSON (Data)", "Markdown (Report)", "Excel (XLSX)"],
            help="Choose the format that best suits your needs"
        )
        
        filter_query = st.text_input(
            "Filter by query (optional)",
            placeholder="e.g., ethics, enlightenment, Plato...",
            help="Leave empty to export entire catalog"
        )
        
        if st.button("📥 Generate Export", type="primary"):
            with st.spinner("Generating export..."):
                # Get entries to export
                if filter_query:
                    results = agent.search(filter_query, max_results=1000)
                    entries = results
                else:
                    entries = [{'entry': e} for e in agent.catalog['entries']]
                
                # Map format names
                format_map = {
                    "CSV (Spreadsheet)": "csv",
                    "BibTeX (LaTeX)": "bibtex",
                    "JSON (Data)": "json",
                    "Markdown (Report)": "markdown",
                    "Excel (XLSX)": "xlsx"
                }
                
                format_code = format_map[export_format]
                export_path = agent.export(entries, format=format_code)
                
                # Read file and offer download
                with open(export_path, 'rb') as f:
                    file_data = f.read()
                
                mime_types = {
                    'csv': 'text/csv',
                    'bibtex': 'text/plain',
                    'json': 'application/json',
                    'markdown': 'text/markdown',
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                }
                
                extensions = {
                    'csv': 'csv',
                    'bibtex': 'bib',
                    'json': 'json',
                    'markdown': 'md',
                    'xlsx': 'xlsx'
                }
                
                st.success(f"✅ Exported {len(entries)} entries to {export_format}")
                
                st.download_button(
                    f"📥 Download {export_format}",
                    file_data,
                    file_name=f"libris_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extensions[format_code]}",
                    mime=mime_types[format_code]
                )
    
    # TAB 5: ABOUT
    with tab5:
        st.header("ℹ️ About LIBRIS")
        
        st.markdown("""
        ### 🏛️ What is LIBRIS?
        
        LIBRIS (Latin for "of books") is an Advanced Librarian AI Agent designed to help educators,
        students, and researchers manage and explore bibliographic collections in philosophy and history.
        
        ### ✨ Key Features
        
        - **Intelligent Search**: Find works using keywords, concepts, themes, or time periods
        - **Document Processing**: Extract bibliographic data from PDFs, Word docs, spreadsheets, and more
        - **Curated Collection**: Start with 74 expertly selected philosophical and historical works
        - **Multi-Format Export**: Export to BibTeX, CSV, JSON, Markdown, or Excel
        - **Theme Detection**: Automatic categorization by philosophical themes
        - **Period Awareness**: Browse by historical era from Ancient to Modern
        
        ### 📚 Base Collection
        
        LIBRIS includes carefully curated works spanning 4,000+ years:
        
        - **Ancient Philosophy**: Plato, Aristotle, Confucius, Laozi
        - **Medieval**: Augustine, Aquinas, Avicenna, Ibn Khaldun
        - **Early Modern**: Descartes, Hobbes, Spinoza, Locke
        - **Enlightenment**: Kant, Rousseau, Hume, Smith
        - **Modern**: Nietzsche, Wittgenstein, Rawls, Sartre
        
        ### 🎯 Use Cases
        
        - **Educators**: Build course syllabi and reading lists
        - **Students**: Manage research bibliographies
        - **Researchers**: Organize literature reviews
        - **Librarians**: Catalog philosophical collections
        
        ### 🤝 Created By
        
        **Claude** (Anthropic AI) in collaboration with **Professor Plato**  
        Indiana University, Luddy School of Informatics, Computing, and Engineering
        
        ### 📖 Learn More
        
        - [GitHub Repository](https://github.com/yourusername/libris)
        - [Documentation](https://github.com/yourusername/libris/blob/main/README.md)
        - [Report Issues](https://github.com/yourusername/libris/issues)
        
        ### 📄 License
        
        LIBRIS is open-source educational software.
        
        ---
        
        **Version**: 1.0  
        **Last Updated**: February 2026
        """)


if __name__ == "__main__":
    main()
