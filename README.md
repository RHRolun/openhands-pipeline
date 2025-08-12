# Onboarding an OpenShift Pipeline to create a OpenShift Pull Request

This repository contains the configuration for the OpenHands AI services pipelines.

This project was scaffolded by the CAI team.

## Getting Started

To get started with the OpenHands pipelines, you will need to have a Kubernetes cluster with Tekton and OpenShift Pipelines installed.

### Prerequisites

* A Kubernetes cluster
* `kubectl` configured to connect to your cluster
* Tekton Pipelines installed
* OpenShift Pipelines installed

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/redhat-rh-is-all-hands-dev/openhands-pipelines.git
   ```
2. Apply the general setup:
   ```bash
   kubectl apply -f general-setup/
   ```
3. Apply the desired pipeline:
   * For the Issue Resolver pipeline:
     ```bash
     kubectl apply -f issue-resolver-pipeline/
     ```
   * For the Coherence pipeline:
     ```bash
     kubectl apply -f coherence-pipeline/
     ```

## Directory Structure

* `coherence-pipeline/`: Contains the Tekton resources for the Coherence pipeline. See [coherence-pipeline/README.md](coherence-pipeline/README.md) for more information.
* `general-setup/`: Contains general setup resources, such as secrets.
* `issue-resolver-pipeline/`: Contains the Tekton resources for the Issue Resolver pipeline. See [issue-resolver-pipeline/README.md](issue-resolver-pipeline/README.md) for more information.
* `mcp-git-server/`: Contains the resources for the MCP git server.

## Contributing

We welcome contributions to the OpenHands pipelines! Please see our [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
