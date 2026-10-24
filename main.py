import os
import sys
import logging
from groq import Groq

# Configure logging for clear output in GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

IGNORE_DIRS = [
    ".git", ".venv", "venv", "__pycache__", ".pyc", "node_modules", 
    "dist", "build", ".idea", ".vscode", "package-lock.json", "poetry.lock"
]

IGNORE_EXTENSIONS = [
    ".png", ".jpg", ".ico", ".mp4", ".gif", ".zip", ".tar", 
    ".exe", ".pdf", ".env"
]

VALID_EXTENSIONS = [
    ".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c", 
    ".rb", ".php", ".md", ".html", ".css", ".json", ".yml", 
    ".yaml", ".sh", ".bat", ".toml", ".env.example"
]


def check_codebase(root_dir="."):
    code_content = {}
    logger.info(f"Walking through directory: {root_dir}")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for file in filenames:
            if os.path.splitext(file)[1] in IGNORE_EXTENSIONS:
                continue

            _, ext = os.path.splitext(file)
            if ext in VALID_EXTENSIONS or file in ["requirements.txt", "package.json"]:
                file_path = os.path.join(dirpath, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code_content[file_path] = f.read()
                except UnicodeDecodeError:
                    continue

    logger.info(f"Successfully read {len(code_content)} code files.")
    return code_content


SYSTEM_PROMPT = """
You are an expert software engineer and elite technical writer. You can analyze any codebase, understand its architecture, features, and dependencies, and generate comprehensive, professional documentation.

Your task is to analyze the provided code files and generate a complete, well-formatted `README.md` file in Markdown. 

Your output must be strictly the Markdown content (no conversational filler, no extra text outside the markdown block). 

Include the following sections based on the codebase:

### Core & Mandatory Sections
- **Project Title & Badges:** A clear, professional project title, brief description, and relevant badges.
- **Description:** A concise explanation of what the project does, the problem it solves, and why it exists.
- **Table of Contents:** An outline for quick navigation.
- **Tech Stack / Built With:** The languages, frameworks, libraries, and tools used.
- **Prerequisites & Installation:** Step-by-step installation commands and environment setup instructions.
- **Run Locally / Usage:** Clear code snippets, instructions, or commands showing how to run and use the project.
- **License:** Statement of user and modification rights.
- **Authors & Acknowledgements:** Credit to creators, contributors, and inspirations.

### Include These Custom Sections Where Applicable
- **API Reference:** Endpoints, methods, and parameters if applicable.
- **Environment Variables:** Required `.env` keys and configuration parameters.
- **Features:** Key highlights and capabilities.
- **Roadmap:** Future plans or scaling goals.
- **Contributing:** Guidelines for contributors.
- **Support / FAQ:** Troubleshooting or contact details.

Ensure formatting uses clean Markdown syntax, code blocks, and professional technical terminology.
"""


def code_to_api(code_content, api_key, workspace_path):
    if not code_content:
        logger.warning("No valid code files found to analyze!")
        return

    formatted_code = ""
    for file_path, content in code_content.items():
        formatted_code += f"\n\n--- FILE: {file_path} ---\n{content}"

    USER_PROMPT = f"""
    You are provided with the following code files from a project:
    {formatted_code}
    
    Analyze them to understand the architecture, features, and dependencies. 
    Generate a complete, professional `README.md` in Markdown format that includes all the sections outlined in the system prompt.
    """

    logger.info("Sending codebase to Groq LLM to generate README...")

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

    readme_output_path = os.path.join(workspace_path, "README.md")
    with open(readme_output_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    logger.info(f"Success! README.md has been generated and saved to {readme_output_path}")


def main():
    # 1. Grab API key passed from action.yml arguments or environment fallback
    api_key = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("Error: Groq API key not provided.")
        sys.exit(1)

    # 2. Get the workspace path where the target repository is checked out
    workspace_path = os.getenv("GITHUB_WORKSPACE", ".")
    logger.info(f"Scanning repository workspace at: {workspace_path}")

    # 3. Run codebase scanner on the target workspace
    code_content = check_codebase(workspace_path)
    logger.info(f"Found {len(code_content)} code files in the codebase.\n")

    # 4. Send to Groq and write README
    code_to_api(code_content, api_key, workspace_path)


if __name__ == "__main__":
    main()