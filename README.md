# OpenHands Pipeline

This repository contains the configuration for the OpenHands pipelines, a project by the CAI team.

## Overview

The repository is structured into the following components:

-   **[coherence-pipeline](#coherence-pipeline):** Contains the configuration for the coherence pipeline.
-   **[issue-resolver-pipeline](#issue-resolver-pipeline):** Holds the setup for the issue resolver pipeline.
-   **[mcp-git-server](#mcp-git-server):** Includes the deployment details for the MCP Git server.
-   **[general-setup](#general-setup):** Provides general setup configurations, including secrets management.

Each directory contains the necessary YAML files for deploying and managing its respective components. For more details on each component, please refer to the specific directories.

## Pipelines

### Coherence Pipeline
The `coherence-pipeline` directory contains the resources for running the coherence pipeline, which ensures that the state of the repository is consistent and up-to-date.

### Issue Resolver Pipeline
The `issue-resolver-pipeline` is designed to automatically address and resolve issues based on predefined criteria.

## Git Server
The `mcp-git-server` directory contains the configurations for deploying a Git server.

## General Setup
The `general-setup` directory contains configurations that are common across all pipelines and components.
