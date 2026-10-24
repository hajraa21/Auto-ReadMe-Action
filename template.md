# To use this automation:
 1. In your repo (folder) create a new file at this exact path:
    .github/workflows/generate_readme.yml

 2. In that file, paste this exact template:
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

 3. In Github, open the current repo's setting -> secrets and variables -> actions, then create a new repo secret and add the GROQ_API_KEY there.

 4. That's it, now you can run your workflow from the actions tab and you will have a pull request which you can merge and get your README.