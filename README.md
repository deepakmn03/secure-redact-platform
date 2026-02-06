# Secure Redact Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.23-red)

A production-grade, API-first platform for securely redacting sensitive information from PDF documents. 

Unlike basic tools that simply draw black rectangles over text (masking), this engine performs **True Redaction**: it permanently removes the text data, vector graphics, and metadata from the file structure, rendering the redacted information irretrievable.

## 🚀 Key Features

* **True Redaction:** Destructive editing of the PDF content stream to prevent reverse-engineering.
* **Metadata Scrubbing:** Automatically removes author, creator, and title metadata to prevent data leakage.
* **Vector Cleanup:** Removes underlying images or vector graphics in the redacted area.
* **Case Insensitive Search:** Robust detection of target words regardless of casing.
* **High Performance:** Built on `PyMuPDF` (C++ bindings) and `FastAPI` for asynchronous processing.
* **Auto-Cleanup:** Background tasks ensure sensitive uploaded/processed files are immediately deleted after delivery.

## 🛠️ Tech Stack

* **Core Engine:** Python 3.10+, PyMuPDF (Fitz)
* **API Framework:** FastAPI, Uvicorn
* **Process Management:** Python BackgroundTasks for resource cleanup

## ⚡ Quick Start

### Prerequisites
* Python 3.10 or higher
* Git

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/secure-redact-platform.git](https://github.com/YOUR_USERNAME/secure-redact-platform.git)
    cd secure-redact-platform
    ```

2.  **Create a Virtual Environment**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Server

Start the application in development mode:

```bash
uvicorn main:app --reload