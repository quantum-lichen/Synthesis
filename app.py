import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import numpy as np
from collections import Counter, defaultdict
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration de la page
st.set_page_config(
    page_title="Nordique Analyzer",
    page_icon="🧠",
    layout="wide"
)

def extract_pdf_text(file):
    """Extrait le texte d'un fichier PDF"""
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF: {str(e)}")
        return ""

def extract_sentences(text):
    """Extrait les phrases d'un texte"""
    # Nettoyage basique
    text = re.sub(r'\s+', ' ', text).strip()
    # Découpage en phrases
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences

def calculate_similarity_matrix(documents):
    """Calcule la matrice de similarité entre documents"""
    if len(documents) < 2:
        return None
    
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return similarity_matrix
    except:
        return None

def analyze_documents(documents):
    """Analyse les consensus et discordances entre documents"""
    
    # Extraire toutes les phrases de tous les documents
    all_sentences_by_doc = []
    for doc in documents:
        sentences = extract_sentences(doc)
        all_sentences_by_doc.append(sentences)
    
    # Aplatir toutes les phrases
    all_sentences = []
    sentence_to_doc = []
    for doc_idx, sentences in enumerate(all_sentences_by_doc):
        for sentence in sentences:
            all_sentences.append(sentence)
            sentence_to_doc.append(doc_idx)
    
    if len(all_sentences) < 2:
        return None
    
    # Calculer les similarités entre phrases
    vectorizer = TfidfVectorizer(max_features=50, stop_words='english', min_df=1)
    try:
        tfidf_matrix = vectorizer.fit_transform(all_sentences)
    except:
        return {
            "consensus": {},
            "discordances": {},
            "statistics": {
                "total_docs": len(documents),
                "consensus_rate": 0,
                "avg_similarity": 0
            },
            "similarity_matrix": None
        }
    
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Identifier les phrases consensuelles (similaires dans plusieurs documents)
    consensus_phrases = []
    discordance_phrases = []
    
    analyzed_phrases = set()
    
    for i, sentence in enumerate(all_sentences):
        if sentence in analyzed_phrases:
            continue
        
        doc_i = sentence_to_doc[i]
        
        # Trouver les phrases similaires dans d'autres documents
        similar_docs = set()
        similarity_scores = []
        
        for j, other_sentence in enumerate(all_sentences):
            if i != j:
                doc_j = sentence_to_doc[j]
                sim_score = similarity_matrix[i][j]
                
                if sim_score > 0.3 and doc_i != doc_j:  # Seuil de similarité
                    similar_docs.add(doc_j)
                    similarity_scores.append(sim_score)
        
        if len(similar_docs) >= max(1, len(documents) // 2):  # Consensus
            consensus_phrases.append({
                "phrase": sentence,
                "support_docs": len(similar_docs) + 1,
                "avg_similarity": np.mean(similarity_scores) if similarity_scores else 0,
                "source_doc": doc_i
            })
            analyzed_phrases.add(sentence)
    
    # Calculer la similarité globale entre documents
    doc_similarity = calculate_similarity_matrix(documents)
    
    # Identifier les discordances (phrases uniques ou contradictoires)
    for doc_idx, sentences in enumerate(all_sentences_by_doc):
        for sentence in sentences[:3]:  # Prendre les premières phrases de chaque doc
            if sentence not in analyzed_phrases:
                discordance_phrases.append({
                    "phrase": sentence,
                    "source_doc": doc_idx,
                    "uniqueness": 1.0
                })
    
    # Trier par pertinence
    consensus_phrases = sorted(consensus_phrases, key=lambda x: x["avg_similarity"], reverse=True)[:10]
    discordance_phrases = sorted(discordance_phrases, key=lambda x: x["uniqueness"], reverse=True)[:10]
    
    # Calculer les statistiques
    avg_similarity = np.mean(doc_similarity) if doc_similarity is not None else 0
    
    report = {
        "consensus": consensus_phrases,
        "discordances": discordance_phrases,
        "statistics": {
            "total_docs": len(documents),
            "consensus_rate": len(consensus_phrases) / max(1, len(consensus_phrases) + len(discordance_phrases)),
            "avg_similarity": float(avg_similarity)
        },
        "similarity_matrix": doc_similarity
    }
    
    return report

def plot_similarity_heatmap(similarity_matrix, num_docs):
    """Crée une heatmap de similarité entre documents"""
    if similarity_matrix is None:
        return None
    
    labels = [f"Doc {i+1}" for i in range(num_docs)]
    
    fig = go.Figure(data=go.Heatmap(
        z=similarity_matrix,
        x=labels,
        y=labels,
        colorscale='RdYlGn',
        text=np.round(similarity_matrix, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Similarité")
    ))
    
    fig.update_layout(
        title="Matrice de Similarité entre Documents",
        xaxis_title="Documents",
        yaxis_title="Documents",
        height=400
    )
    
    return fig

def plot_consensus_chart(report):
    """Crée un graphique des consensus et discordances"""
    
    # Préparer les données
    data = []
    
    for item in report["consensus"][:5]:
        data.append({
            "Phrase": item["phrase"][:50] + "...",
            "Support": item["support_docs"],
            "Type": "Consensus"
        })
    
    for item in report["discordances"][:5]:
        data.append({
            "Phrase": item["phrase"][:50] + "...",
            "Support": 1,
            "Type": "Discordance"
        })
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df,
        x="Support",
        y="Phrase",
        color="Type",
        orientation='h',
        title="Top 5 Consensus et Discordances",
        color_discrete_map={"Consensus": "#2ecc71", "Discordance": "#e74c3c"}
    )
    
    fig.update_layout(height=400, showlegend=True)
    
    return fig

def generate_pdf_report(report):
    """Génère un rapport PDF"""
    pdf = FPDF()
    pdf.add_page()
    
    # Titre
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Rapport d'Analyse - Consensus/Discordance", ln=True, align='C')
    pdf.ln(10)
    
    # Statistiques
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Statistiques Globales", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Nombre de documents analyses: {report['statistics']['total_docs']}", ln=True)
    pdf.cell(0, 8, f"Taux de consensus: {report['statistics']['consensus_rate']*100:.1f}%", ln=True)
    pdf.cell(0, 8, f"Similarite moyenne: {report['statistics']['avg_similarity']*100:.1f}%", ln=True)
    pdf.ln(10)
    
    # Consensus
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Points de Consensus", ln=True)
    pdf.set_font("Arial", '', 9)
    
    for idx, item in enumerate(report["consensus"][:5], 1):
        phrase = item["phrase"][:80].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, f"{idx}. {phrase} (Support: {item['support_docs']} docs)")
        pdf.ln(2)
    
    pdf.ln(5)
    
    # Discordances
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Points de Discordance", ln=True)
    pdf.set_font("Arial", '', 9)
    
    for idx, item in enumerate(report["discordances"][:5], 1):
        phrase = item["phrase"][:80].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, f"{idx}. {phrase}")
        pdf.ln(2)
    
    # Générer le PDF
    pdf_output = pdf.output(dest="S").encode("latin-1", errors='ignore')
    
    return pdf_output

def load_example_docs():
    """Charge des documents d'exemple"""
    example_docs = [
        """Le réchauffement climatique est une réalité scientifique indéniable. 
        Les températures moyennes mondiales ont augmenté de plus de 1°C depuis l'ère préindustrielle.
        Les énergies renouvelables sont essentielles pour réduire les émissions de CO2.
        L'action climatique doit être une priorité pour tous les gouvernements.""",
        
        """Le changement climatique représente un défi majeur pour l'humanité.
        Les émissions de gaz à effet de serre doivent être réduites rapidement.
        Les énergies renouvelables comme le solaire et l'éolien sont des solutions viables.
        La transition énergétique nécessite des investissements massifs.""",
        
        """Certains contestent l'urgence du réchauffement climatique.
        Les coûts de la transition énergétique sont trop élevés pour l'économie.
        Les énergies fossiles restent nécessaires pour maintenir la croissance économique.
        Les modèles climatiques sont incertains et parfois contradictoires.""",
        
        """L'innovation technologique peut résoudre la crise climatique.
        Les énergies renouvelables deviennent de plus en plus compétitives.
        La collaboration internationale est cruciale pour lutter contre le changement climatique.
        Les entreprises doivent adopter des pratiques durables."""
    ]
    return example_docs

def main():
    # En-tête
    st.title("🧠 Nordique Analyzer")
    st.markdown("### Analyse de Consensus et Discordances entre Documents")
    st.markdown("---")
    
    # Instructions
    with st.expander("ℹ️ Comment utiliser cette application"):
        st.write("""
        1. **Uploadez vos documents** (TXT ou PDF) ou essayez l'exemple
        2. **Cliquez sur Analyser** pour lancer l'analyse
        3. **Consultez les résultats** : consensus, discordances, et visualisations
        4. **Téléchargez le rapport** en PDF si besoin
        """)
    
    # Colonnes pour les boutons
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "📁 Choisissez vos fichiers (TXT ou PDF)",
            type=["txt", "pdf"],
            accept_multiple_files=True
        )
    
    with col2:
        use_example = st.button("🎯 Essayer un exemple", use_container_width=True)
    
    # Bouton d'analyse
    analyze_button = st.button("🔍 Analyser les Documents", type="primary", use_container_width=True)
    
    # Logique d'analyse
    documents = []
    
    if use_example:
        documents = load_example_docs()
        st.success(f"✅ {len(documents)} documents d'exemple chargés!")
    
    elif analyze_button and uploaded_files:
        with st.spinner("📖 Lecture des documents..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.type == "application/pdf":
                    text = extract_pdf_text(uploaded_file)
                else:
                    text = uploaded_file.read().decode("utf-8", errors='ignore')
                
                if text:
                    documents.append(text)
        
        st.success(f"✅ {len(documents)} documents chargés!")
    
    elif analyze_button and not uploaded_files:
        st.warning("⚠️ Veuillez d'abord uploader des fichiers ou essayer l'exemple!")
    
    # Analyser les documents
    if documents:
        with st.spinner("🔬 Analyse en cours..."):
            report = analyze_documents(documents)
        
        if report is None:
            st.error("❌ Erreur lors de l'analyse. Vérifiez vos documents.")
            return
        
        st.markdown("---")
        st.markdown("## 📊 Résultats de l'Analyse")
        
        # Statistiques globales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📚 Documents Analysés",
                report['statistics']['total_docs']
            )
        
        with col2:
            st.metric(
                "🤝 Taux de Consensus",
                f"{report['statistics']['consensus_rate']*100:.1f}%"
            )
        
        with col3:
            st.metric(
                "📈 Similarité Moyenne",
                f"{report['statistics']['avg_similarity']*100:.1f}%"
            )
        
        st.markdown("---")
        
        # Visualisations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Consensus vs Discordances")
            chart = plot_consensus_chart(report)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        with col2:
            st.markdown("### 🔥 Matrice de Similarité")
            heatmap = plot_similarity_heatmap(
                report['similarity_matrix'],
                report['statistics']['total_docs']
            )
            if heatmap:
                st.plotly_chart(heatmap, use_container_width=True)
        
        st.markdown("---")
        
        # Détails des résultats
        tab1, tab2 = st.tabs(["✅ Points de Consensus", "⚠️ Points de Discordance"])
        
        with tab1:
            st.markdown("### Points de Consensus Identifiés")
            if report["consensus"]:
                for idx, item in enumerate(report["consensus"], 1):
                    with st.container():
                        st.markdown(f"**{idx}.** {item['phrase']}")
                        st.caption(f"🔹 Support: {item['support_docs']} documents | Similarité: {item['avg_similarity']:.2%}")
                        st.markdown("---")
            else:
                st.info("Aucun consensus significatif détecté.")
        
        with tab2:
            st.markdown("### Points de Discordance Identifiés")
            if report["discordances"]:
                for idx, item in enumerate(report["discordances"], 1):
                    with st.container():
                        st.markdown(f"**{idx}.** {item['phrase']}")
                        st.caption(f"🔸 Document source: {item['source_doc'] + 1}")
                        st.markdown("---")
            else:
                st.info("Aucune discordance majeure détectée.")
        
        # Bouton de téléchargement PDF
        st.markdown("---")
        st.markdown("### 📥 Télécharger le Rapport")
        
        pdf_output = generate_pdf_report(report)
        
        st.download_button(
            label="📄 Télécharger le Rapport PDF",
            data=pdf_output,
            file_name="rapport_consensus_discordance.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Nordique Analyzer v1.0 | Analyse intelligente de documents"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
