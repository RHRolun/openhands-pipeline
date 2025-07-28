# OpenHands Pipeline

This directory contains Kubernetes manifests for running OpenHands AI-powered pipelines using Tekton, including issue resolution and README standardization across GitHub repositories.

## Files

### Core Pipeline Files

- **`openhands-issue-resolver-pipeline.yaml`** - Main Tekton pipeline that processes GitHub issues using OpenHands AI agent
  - Clones repository from GitHub
  - Runs OpenHands issue resolver to analyze and fix issues
  - Creates draft pull requests with solutions

- **`openhands-readme-standardizer-pipeline.yaml`** - Pipeline for standardizing README files across organization repositories
  - Compares README files against a reference style
  - Applies consistent formatting and structure
  - Maintains repository-specific content

### Automation & Scheduling

- **`issue-resolver-cron-job.yaml`** - Kubernetes Job for triggering pipelines across multiple repositories
  - Reads repository list from ConfigMap
  - Triggers pipeline runs for each configured repository
  - Handles DNS-compliant resource naming

- **`issue-resolver-configmap.yaml`** - ConfigMap containing repository configuration
  - Lists repositories to process
  - Configurable via kubectl

- **`cron-service-account.yaml`** - Service account for automated pipeline triggering
  - Required permissions for creating pipeline runs
  - Used by the cron job

### Security & RBAC

- **`secrets.yaml`** - Kubernetes Secret containing sensitive credentials
  - `llm-api-key`: API key for LLM provider (OpenRouter/OpenAI)
  - `pat-token`: GitHub Personal Access Token for repository access

- **`pipeline-role.yaml`** - RBAC Role defining permissions for pipeline execution
  - Manages pods (create, get, list, watch, delete, patch, update)
  - Manages persistent volume claims

- **`pipeline-rolebinding.yaml`** - Binds the pipeline role to the pipeline service account

## Pipeline Parameters

### Issue Resolver Pipeline
- `repo-url`: GitHub repository URL to process
- `issue-number`: Specific issue number to resolve (optional)
- `llm-model`: AI model to use (default: Qwen)
- `max-iterations`: Maximum processing iterations
- `username`: GitHub username for authentication
- `event-type`: Type of event triggering the pipeline
- `repo-full-name`: Full repository name (owner/repo)
- `namespace`: Kubernetes namespace for execution

### README Standardizer Pipeline
- `org-name`: GitHub organization name
- `reference-repo`: Repository with reference README style
- `llm-model`: AI model to use
- `llm-base-url`: Base URL for the LLM API
- `max-iterations`: Maximum processing iterations
- `username`: GitHub username for authentication
- `namespace`: Kubernetes namespace for execution

## Usage

### Initial Setup

1. Update `secrets.yaml` with your actual API keys and tokens
2. Apply the RBAC manifests: `kubectl apply -f pipeline-role.yaml pipeline-rolebinding.yaml cron-service-account.yaml`
3. Apply secrets: `kubectl apply -f secrets.yaml`
4. Apply the pipelines: `kubectl apply -f openhands-issue-resolver-pipeline.yaml openhands-readme-standardizer-pipeline.yaml`

### Manual Pipeline Execution

For issue resolution:
```bash
tkn pipeline start openhands-issue-resolver-pipeline \
  --param repo-url="https://github.com/owner/repo.git" \
  --param issue-number="123" \
  --param username="your-username" \
  --param namespace="openhands-pipeline"
```

For README standardization:
```bash
tkn pipeline start openhands-readme-standardizer-pipeline \
  --param org-name="your-org" \
  --param reference-repo="your-org/reference-repo" \
  --param username="your-username" \
  --param namespace="openhands-pipeline"
```

### Automated Execution

1. Configure repositories in `issue-resolver-configmap.yaml`
2. Apply the ConfigMap: `kubectl apply -f issue-resolver-configmap.yaml`
3. Run the cron job: `kubectl create job --from=job/start-issue-resolver-pipelines manual-trigger`