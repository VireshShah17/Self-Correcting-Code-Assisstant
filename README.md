# 🤖 Self-Correcting Code Assistant

An autonomous AI agent that writes, tests, validates, and fixes its own Python code. This intelligent assistant leverages large language models to generate code based on your requirements and automatically corrects errors through iterative refinement.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Clone the Repository](#clone-the-repository)
- [Setup on Local System](#setup-on-local-system)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Autonomous Code Generation**: AI-powered generation of Python scripts based on natural language descriptions
- **Self-Correcting Logic**: Automatically detects and fixes errors in generated code
- **Test-Driven Development**: Generates test cases (assert statements) to validate the code
- **AST Validation**: Validates Python syntax before execution
- **Interactive UI**: User-friendly Streamlit interface for submitting tasks and viewing results
- **Real-time Feedback**: Live updates showing each step of the agent's process

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **pip** - Usually comes with Python

## 🔧 Clone the Repository

```bash
git clone https://github.com/VireshShah17/Self-Correcting-Code-Assisstant.git
cd self-correcting-code-assisstant
```

## 🚀 Setup on Local System

### 1. Create a Virtual Environment

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including Streamlit, LangChain, Groq client, and other dependencies.

## 🔐 Environment Variables

After cloning the repository, you need to create an environment file to store your credentials.

### 1. Create a `.env` file

In the root directory of the project, create a file named `.env`:

```bash
touch .env
```

### 2. Add Your Credentials

Open the `.env` file and add your API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

Replace `your_groq_api_key_here` with your actual Groq API key. You can obtain a free API key from [Groq's website](https://console.groq.com).

**Important**: Never commit the `.env` file to version control. It's already listed in `.gitignore`.

## ▶️ Running the Application

Once the setup is complete, run the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your default web browser.

### How to Use

1. Enter your coding task in the text area (e.g., "Write a function that calculates the factorial of a number and include assert statements to test it")
2. Click the **"🚀 Generate & Run"** button
3. Watch as the AI agent:
   - Generates Python code
   - Validates the syntax
   - Executes the code
   - Auto-corrects any errors
4. View the results and feedback in real-time

## 🤝 Contributing

We welcome contributions from the community! If you find any issues or have ideas for new features, please feel free to contribute.

### How to Contribute

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/self-correcting-code-assisstant.git
   ```
3. **Create a new branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add your meaningful commit message"
   ```
5. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** on the original repository with a clear description of your changes

### Issues

If you encounter any bugs or have suggestions for improvements, please [open an issue](https://github.com/VireshShah17/Self-Correcting-Code-Assisstant/issues) on GitHub.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy coding! 🎉**
