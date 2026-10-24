# Auto‑Readme Action 🤖  
**Automatically generate a professional `README.md` for any repository using Groq LLM.**  

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/hajraa21/auto-readme-action/generate_readme.yml?branch=main&label=CI)](https://github.com/hajraa21/auto-readme-action/actions)  
[![License](https://img.shields.io/github/license/hajraa21/auto-readme-action)](LICENSE)  
[![Docker Image Size](https://img.shields.io/docker/image-size/hajraa21/auto-readme-action/latest)](https://hub.docker.com/r/hajraa21/auto-readme-action)  

---  

## Description  

`auto-readme-action` is a **GitHub Action** that scans the source code of the repository it runs in, sends the collected files to a Groq LLM (GPT‑OSS‑120B), and writes a freshly generated `README.md`.  
It eliminates the manual effort of keeping documentation up‑to‑date and guarantees a consistent, high‑quality format every time code changes are pushed.

### Why it exists  

- Documentation often lags behind code changes.  
- Writing a comprehensive README is time‑consuming and error‑prone.  
- Leveraging a powerful LLM lets you produce human‑readable, structured docs automatically.  

---  

## Table of Contents  

- [Tech Stack / Built With](#tech-stack--built-with)  
- [Features](#features)  
- [Prerequisites & Installation](#prerequisites--installation)  
- [Usage](#usage)  
  - [1️⃣ Add the workflow file](#1️⃣-add-the-workflow-file)  
  - [2️⃣ Configure secrets](#2️⃣-configure-secrets)  
  - [3️⃣ Run the workflow](#3️⃣-run-the-workflow)  
  - [Run locally (Docker)](#run-locally-docker)  
- [Environment Variables](#environment-variables)  
- [API Reference](#api-reference)  
- [Roadmap](#roadmap)  
- [Contributing](#contributing)  
- [Support / FAQ](#support--faq)  
- [License](#license)  
- [Authors & Acknowledgements](#authors--acknowledgements)  

---  

## Tech Stack / Built With  

| Category | Tool / Library |
|----------|----------------|
| **Language** | Python ≥ 3.13 |
| **LLM Provider** | Groq (`groq` Python SDK) |
| **Model** | `openai/gpt-oss-120b` |
| **Containerisation** | Docker (used by the Action) |
| **CI / Automation** | GitHub Actions |
| **Dependency Management** | `pyproject.toml` (PEP 621) |
| **Utilities** | `python-dotenv`, `requests` |
| **GitHub Action Helper** | `peter-evans/create-pull-request` (for PR creation) |

---  

## Features  

- **Full repository scan** – walks the workspace, reads all source files while respecting ignore lists (`.git`, `node_modules`, etc.).  
- **Smart file filtering** – only includes relevant extensions (`.py`, `.js`, `.md`, …) and common manifest files (`requirements.txt`, `package.json`).  
- **LLM‑driven documentation** – prompts Groq’s GPT‑OSS‑120B to produce a complete, markdown‑formatted README.  
- **Docker‑based Action** – runs in an isolated container, no host‑side dependencies required.  
- **Automatic PR creation** – integrates with `peter-evans/create-pull-request` to open a PR with the updated README.  
- **Configurable via secrets** – Groq API key is supplied securely through GitHub Secrets.  

---  

## Prerequisites & Installation  

1. **Groq API key** – sign up at <https://groq.com> and obtain a key.  
2. **GitHub repository** – the action runs inside any repo you own or contribute to.  
3. **Docker** – required only for local testing of the Action (GitHub Actions provide Docker automatically).  

No additional local installation is needed; the Action is consumed via a workflow file.

---  

## Usage  

### 1️⃣ Add the workflow file  

Create `.github/workflows/generate_readme.yml` in your repository with the following content:

```yaml
name: Auto-Generate README

on:
  push:
    branches: [ main, master ]

permissions:
  contents: write
  pull-requests: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Run Auto-Readme Action
        uses: hajraa21/auto-readme-action@main
        with:
          groq-api-key: ${{ secrets.GROQ_API_KEY }}

      - name: Create Pull Request for README Update
        uses: peter-evans/create-pull-request@v7
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "docs: auto-generate updated README.md via Groq LLM"
          branch: docs/auto-update-readme
          title: "🤖 Automated README Update"
          body: |
            This automated pull request updates the `README.md` based on recent codebase changes. 
            Please review the diff to ensure accuracy before merging!
          author: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
          signoff: false
          delete-branch: true
          add-paths: README.md
```

### 2️⃣ Configure secrets  

1. Go to **Settings → Secrets and variables → Actions** in your repository.  
2. Add a new **Repository secret** named `GROQ_API_KEY` and paste your Groq API key.  

### 3️⃣ Run the workflow  

Push a commit to `main` (or `master`). The workflow will:

1. Checkout the code.  
2. Execute the Docker‑based `auto-readme-action`, which:  
   - Scans the repository.  
   - Sends the collected files to Groq.  
   - Writes `README.md` at the repository root.  
3. Open a pull request (`docs/auto-update-readme`) containing the newly generated README.  

Merge the PR once you verify the content.

### Run locally (Docker)  

```bash
# Build the Docker image
docker build -t auto-readme-action .

# Run the container (replace $GROQ_API_KEY with your key)
docker run --rm \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -v "$(pwd)":/workspace \
  auto-readme-action
```

The command will generate/overwrite `README.md` in the current directory.

---  

## Environment Variables  

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key used by the Action to call the LLM. | ✅ (via secret) |
| `GITHUB_WORKSPACE` | Set automatically by GitHub Actions; points to the checked‑out repository. | ✅ (provided by runner) |

---  

## API Reference  

The Action does **not** expose a public HTTP API. Internally it uses the Groq Python SDK:

```python
from groq import Groq

client = Groq(api_key=api_key)
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
    temperature=0.3,
)

readme_content = response.choices[0].message.content
```

The `readme_content` is written to `README.md` in the repository root.

---  

## Roadmap  

- **Support for additional LLM providers** (OpenAI, Anthropic, etc.).  
- **Configurable ignore patterns** via action inputs.  
- **Incremental updates** – only regenerate sections that changed.  
- **Customizable output template** (choose which sections to include).  
- **CLI wrapper** for local, non‑GitHub usage.  

---  

## Contributing  

Contributions are welcome! Please follow these steps:

1. Fork the repository.  
2. Create a feature branch (`git checkout -b feat/your-feature`).  
3. Make your changes, ensuring code passes linting (`ruff`/`flake8` recommended).  
4. Run the test suite (if added) with `pytest`.  
5. Open a Pull Request describing the change.  

Please adhere to the existing coding style and include documentation updates where appropriate.

---  

## Support / FAQ  

**Q: I get “Error: Groq API key not provided.”**  
A: Ensure the secret `GROQ_API_KEY` is defined in the repository settings and that the workflow references it correctly (`${{ secrets.GROQ_API_KEY }}`).

**Q: The generated README is missing sections.**  
A: The LLM output depends on the prompt and the scanned code. Make sure the repository contains source files with supported extensions and that the `SYSTEM_PROMPT` in `main.py` matches the sections you need.

**Q: Can I run the Action locally?**  
A: Yes. Build the Docker image (`docker build -t auto-readme-action .`) and execute it as shown in the **Run locally (Docker)** section.

**Q: Does this action modify any files other than `README.md`?**  
A: No. It only writes/overwrites `README.md` at the repository root.

For further assistance, open an issue or contact the maintainer.

---  

## License  

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---  

## Authors & Acknowledgements  

- **Hajraa21** – Creator & maintainer of `auto-readme-action`.  
- **Groq** – Providing the LLM inference API used for documentation generation.  
- **peter-evans/create-pull-request** – Action used to open PRs automatically.  

Special thanks to the open‑source community for the libraries listed in `pyproject.toml`.  