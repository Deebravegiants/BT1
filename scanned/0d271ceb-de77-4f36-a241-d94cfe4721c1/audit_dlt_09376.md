# [?] chore(security): fix shell injection security issue (#2954)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2025-10-30
Source: https://github.com/berachain/beacon-kit/commit/2aa1297bc90253a5f5e86292c5d49b1662543fce
Type: security-commit

## Details
chore(security): fix shell injection security issue (#2954)

Co-authored-by: Cal Bera <calbera@berachain.com>

## Patch
### .github/workflows/pipeline.yml
```diff
@@ -197,25 +197,42 @@ jobs:
         uses: actions/checkout@v3
 
       - name: Echo GitHub Context Variables
+        env:
+          GITHUB_ACTOR: ${{ github.actor }}
+          GITHUB_REPOSITORY: ${{ github.repository }}
+          GITHUB_EVENT_NAME: ${{ github.event_name }}
+          GITHUB_SHA: ${{ github.sha }}
+          GITHUB_REF: ${{ github.ref }}
+          GITHUB_WORKFLOW: ${{ github.workflow }}
+          GITHUB_ACTION: ${{ github.action }}
+          GITHUB_RUN_ID: ${{ github.run_id }}
+          GITHUB_RUN_NUMBER: ${{ github.run_number }}
+          GITHUB_JOB: ${{ github.job }}
+          GITHUB_SERVER_URL: ${{ github.server_url }}
+          GITHUB_API_URL: ${{ github.api_url }}
+          GITHUB_GRAPHQL_URL: ${{ github.graphql_url }}
+          GITHUB_HEAD_REF: ${{ github.head_ref }}
+          GITHUB_BASE_REF: ${{ github.base_ref }}
+          PUSH_DOCKER_IMAGE: ${{ env.PUSH_DOCKER_IMAGE }}
+          VERSION: ${{ env.VERSION }}
         run: |
-          echo "GitHub Actor: ${{ github.actor }}"
-          echo "GitHub Repository: ${{ github.repository }}"
-          echo "GitHub Event Name: ${{ github.event_name }}"
-          echo "GitHub SHA: ${{ github.sha }}"
-          echo "GitHub Ref: ${{ github.ref }}"
-          echo "GitHub Workflow: ${{ github.workflow }}"
-          echo "GitHub Action: ${{ github.action }}"
-          echo "GitHub Run ID: ${{ github.run_id }}"
-          echo "GitHub Run Number: ${{ github.run_number }}"
-          echo "GitHub Job: ${{ github.job }}"
-          echo "GitHub Server URL: ${{ github.server_url }}"
-          echo "GitHub API URL: ${{ github.api_url }}"
-          echo "GitHub GraphQL URL: ${{ github.graphql_url }}"
-          echo "Github Ref: ${{ github.ref }}"
-          echo "GitHub Head Ref: ${{ github.head_ref }}"
-          echo "GitHub Base Ref: ${{ github.base_ref }}"
-          echo "PUSH_DOCKER_IMAGE: ${{ env.PUSH_DOCKER_IMAGE }}"
-          echo "VERSION: ${{ env.VERSION }}"
+          echo "GitHub Actor: \"$GITHUB_ACTOR\""
+          echo "GitHub Repository: \"$GITHUB_REPOSITORY\""
+          echo "GitHub Event Name: \"$GITHUB_EVENT_NAME\""
+          echo "GitHub SHA: \"$GITHUB_SHA\""
+          echo "GitHub Ref: \"$GITHUB_REF\""
+          echo "GitHub Workflow: \"$GITHUB_WORKFLOW\""
+          echo "GitHub Action: \"$GITHUB_ACTION\""
+          echo "GitHub Run ID: \"$GITHUB_RUN_ID\""
+          echo "GitHub Run Number: \"$GITHUB_RUN_NUMBER\""
+          echo "GitHub Job: \"$GITHUB_JOB\""
+          echo "GitHub Server URL: \"$GITHUB_SERVER_URL\""
+          echo "GitHub API URL: \"$GITHUB_API_URL\""
+          echo "GitHub GraphQL URL: \"$GITHUB_GRAPHQL_URL\""
+          echo "GitHub Head Ref: \"$GITHUB_HEAD_REF\""
+          echo "GitHub Base Ref: \"$GITHUB_BASE_REF\""
+          echo "PUSH_DOCKER_IMAGE: \"$PUSH_DOCKER_IMAGE\""
+          echo "VERSION: \"$VERSION\""
       - name: Build Docker image
         run: |
           make build-docker
```
