# 🖍 Plenary Protocol Processing Pipeline

Welcome to the **Plenary Protocol Data Pipeline**! This repository provides a structured pipeline to process data from plenary logs. Below is an overview of how to set up and run the pipeline, as well as a description of each stage. �\de80

---

## ⚙️ Customization
This pipeline is fully customizable to fit your requirements:
- **Date Range**: Adjust the fetching parameters to define the desired time period for plenary minutes.
- **Processing Steps**: Modify the scripts for separation, preparation, or evaluation as needed.

---

## 🛠️ Setup and How to Run

### 1. Clone the Repository
Start by cloning this repository to your local machine:
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Set Up the Environment
Install the required dependencies using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Initialize DVC
Initialize DVC (Data Version Control) in the repository:
```bash
dvc init --no-scm
```

### 4. Reproduce the Pipeline
Run the entire pipeline by executing:
```bash
dvc repro
```

---

## 🔗 Pipeline Stages

### 1️⃣ **Fetching**  
📥 **Description**: Downloads plenary minutes for a defined time period.  
- **Input**: Date range parameters.  
- **Output**: A raw CSV file containing plenary minutes.  

---

### 2️⃣ **Separation**  
🔍 **Description**: Splits the contents of the plenary protocols into smaller units, such as speeches or speaker contributions.  
- **Output**: A CSV file with separated units.  

---

### 3️⃣ **Preparation**  
🩹 **Description**: Processes the split units further with steps like:  
- Data cleansing 🩼  
- Formatting 🖍  
- Normalization 🔄  
- **Output**: Cleaned and processed data in a CSV format.  

---

### 4️⃣ **Evaluation**  
📊 **Description**: Evaluates the prepared data for:  
- Analysis 🔍 e.g. wordcount, unique values ✅ 
- **Input**: Processed data from the preparation stage.  
- **Output**: Evaluation reports and analysis stored in the `ressources` folder.  

---

🎉 **Enjoy processing your plenary data!**  
Feel free to contribute, suggest improvements, or raise issues. 🙌

