# 🧠 Nordique Analyzer - Analyse de Consensus/Discordance

Application Streamlit pour analyser les consensus et discordances entre plusieurs documents texte.

## 🎯 Fonctionnalités

- ✅ **Upload multiple de fichiers** (TXT et PDF)
- 🔍 **Analyse automatique** de consensus et discordances
- 📊 **Visualisations interactives** (graphiques, heatmaps)
- 📈 **Matrice de similarité** entre documents
- 📄 **Export PDF** du rapport d'analyse
- 🎯 **Mode exemple** pour tester l'application

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone <votre-repo>
cd nordique-analyzer
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

## 📖 Utilisation

1. **Option 1 - Vos documents** :
   - Cliquez sur "Choisissez vos fichiers"
   - Sélectionnez plusieurs fichiers TXT ou PDF
   - Cliquez sur "Analyser les Documents"

2. **Option 2 - Exemple** :
   - Cliquez sur "Essayer un exemple"
   - L'analyse se lance automatiquement avec des documents de démonstration

3. **Résultats** :
   - Consultez les statistiques globales
   - Visualisez les graphiques de consensus/discordance
   - Explorez la matrice de similarité
   - Lisez les détails des consensus et discordances
   - Téléchargez le rapport PDF

## 🔬 Comment ça marche ?

L'application utilise :
- **TF-IDF** pour vectoriser les textes
- **Cosine Similarity** pour mesurer la similarité entre phrases
- **Clustering logique** pour identifier les consensus (phrases similaires dans plusieurs documents)
- **Détection d'unicité** pour identifier les discordances

### Critères de Consensus
Une phrase est considérée comme un consensus si :
- Elle a une similarité > 0.3 avec des phrases dans d'autres documents
- Elle est supportée par au moins 50% des documents

### Critères de Discordance
Une phrase est considérée comme une discordance si :
- Elle est unique à un document
- Elle n'a pas de phrases similaires dans les autres documents

## 📊 Métriques Calculées

- **Taux de Consensus** : Pourcentage de points d'accord entre documents
- **Similarité Moyenne** : Degré de ressemblance global entre tous les documents
- **Support par Document** : Nombre de documents qui appuient chaque point

## 🛠️ Technologies Utilisées

- **Streamlit** : Interface utilisateur
- **scikit-learn** : Analyse TF-IDF et similarité
- **Plotly** : Visualisations interactives
- **PyPDF2** : Extraction de texte des PDFs
- **FPDF** : Génération de rapports PDF

## 📦 Structure du Projet

```
nordique-analyzer/
│
├── app.py                 # Application principale
├── requirements.txt       # Dépendances Python
├── README.md             # Documentation
└── .streamlit/
    └── config.toml       # Configuration Streamlit
```

## 🌐 Déploiement sur Streamlit Cloud

1. **Créer un compte** sur [Streamlit Cloud](https://streamlit.io/cloud)

2. **Connecter votre dépôt GitHub** :
   - New app > From existing repo
   - Sélectionner votre repository
   - Branch: main
   - Main file path: app.py

3. **Déployer** : L'application sera automatiquement déployée !

## 🎨 Personnalisation

### Modifier le seuil de similarité

Dans `app.py`, ligne ~90 :
```python
if sim_score > 0.3:  # Modifier ce seuil (0.0 à 1.0)
```

### Ajuster le nombre de résultats affichés

Dans `app.py`, ligne ~117 :
```python
consensus_phrases = sorted(...)[:10]  # Modifier le nombre
```

## 🐛 Dépannage

### Erreur : "No module named 'PyPDF2'"
```bash
pip install PyPDF2
```

### Erreur : "Failed to load PDF"
- Vérifiez que votre PDF n'est pas protégé par mot de passe
- Essayez de le convertir en TXT

### L'application ne se lance pas
```bash
streamlit cache clear
streamlit run app.py
```

## 📝 Exemples d'Utilisation

### Cas d'usage 1 : Analyse de sondages
Comparez les réponses de différents groupes à des questions ouvertes

### Cas d'usage 2 : Revue de littérature
Identifiez les consensus et débats dans des articles scientifiques

### Cas d'usage 3 : Analyse de feedback
Trouvez les points communs et divergences dans les retours clients

### Cas d'usage 4 : Comparaison de politiques
Analysez les similitudes et différences entre documents officiels

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Reporter des bugs
- Suggérer des améliorations
- Proposer de nouvelles fonctionnalités


## 👨‍💻 Auteur

Créé avec ❤️ pour l'analyse intelligente de documents

---

**Note** : Pour de meilleurs résultats, utilisez des documents avec un contenu substantiel (plus de 100 mots chacun) et sur des sujets connexes.
