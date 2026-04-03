# AU Customer-Agent Simulator (Wavfile Generator App)

A high-performance, minimalist web application built with Streamlit that generates Australian-accented dialogue scripts and audio files.

## 🚀 Overview

This application streamlines the creation of training data or simulations by:
1.  **Crawling a Website**: Using Gemini 3 Flash to understand brand tone and context from a provided URL.
2.  **Generating Scripts**: Creating realistic 2-speaker dialogues (Agent/Customer) based on a specific scenario.
3.  **Synthesizing Audio**: Converting scripts into multi-speaker WAV files using Google Cloud Text-to-Speech with natural Australian English voices.
4.  **Secure Storage**: Uploading the final audio to a Google Cloud Storage bucket and providing a signed temporary download link.

## 🎨 Design Philosophy

Adheres to a strict **Minimalist Flat Aesthetic**:
-   Zero gradients, shadows, or rounded corners.
-   High-contrast, distraction-free interface.
-   Single-column, centered layout for maximum clarity.

## 🛠 Prerequisites

To use this app, you will need a Google Cloud Platform (GCP) project with the following APIs enabled:
-   **Vertex AI API** (for script generation)
-   **Cloud Text-to-Speech API** (for audio synthesis)
-   **Cloud Storage** (for file hosting)

## 📦 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ssreevalsam40/wavfile-generator-app.git
    cd wavfile-generator-app
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 🖥 Usage

Run the Streamlit application:
```bash
streamlit run main.py
```

### Configuration
The app uses a **"Bring Your Own Credentials"** model. In the sidebar:
-   Enter your **GCP Project ID**.
-   Provide a **GCS Bucket Name**.
-   Upload your **Service Account JSON key** (processed in-memory only).

## 🔒 Security

-   **No Hardcoded Keys**: Sensitive information like Service Account keys and `.env` files are ignored by Git.
-   **In-Memory Processing**: Uploaded keys are never stored on the server disk; they are cleared upon session termination.

## 📜 License

[MIT](LICENSE)
