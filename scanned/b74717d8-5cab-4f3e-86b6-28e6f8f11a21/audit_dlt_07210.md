# [?] Merge pull request from GHSA-cq9g-c286-6ch7

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-11-29
Source: https://github.com/solana-labs/solana/commit/a665d679cc1439ddbc5ee505a2537eb00f437a60
Type: security-commit

## Details
Merge pull request from GHSA-cq9g-c286-6ch7

* create a reusable workflow for current error reporting logic

* make github.event.head_commit.message as a env, COMMIT_MESSAGE

* make github.event.head_commit.author.name as a env, COMMIT_AUTHOR_NAME

* remove redundant name

* replace error reporting step with the reusalble workflow

## Patch
### .github/workflows/client-targets.yml
```diff
@@ -68,18 +68,6 @@ jobs:
       - android
       - ios
     if: failure() && github.event_name == 'push'
-    runs-on: ubuntu-20.04
-    steps:
-      - name: Slack
-        run: |
-          curl -H "Content-Type: application/json" \
-            -X POST ${{ secrets.SLACK_ERROR_REPORTING_WEBHOOK }} \
-            -d '{
-              "attachments": [
-                {
-                  "color": "#AC514C",
-                  "text":
-                    "*${{ github.repository }} (${{ github.workflow }})*\n${{ github.event.head_commit.message }} - _${{ github.event.head_commit.author.name }}_\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Build>",
-                }
-              ]
-            }'
+    uses: ./.github/workflows/error-reporting.yml
+    secrets:
+      WEBHOOK: ${{ secrets.SLACK_ERROR_REPORTING_WEBHOOK }}
```

### .github/workflows/docs.yml
```diff
@@ -93,18 +93,6 @@ jobs:
       - check
       - build_and_deploy
     if: failure() && github.event_name == 'push'
-    runs-on: ubuntu-20.04
-    steps:
-      - name: Slack
-        run: |
-          curl -H "Content-Type: application/json" \
-            -X POST ${{ secrets.SLACK_ERROR_REPORTING_WEBHOOK }} \
-            -d '{
-              "attachments": [
-                {
-                  "color": "#AC514C",
-                  "text":
-                    "*${{ github.repository }} (${{ github.workflow }})*\n${{ github.event.head_commit.message }} - _${{ github.event.head_commit.author.name }}_\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Build>",
-                }
-              ]
-            }'
+    uses: ./.github/workflows/error-reporting.yml
+    secrets:
+      WEBHOOK: ${{ secrets.SLACK_ERROR_REPORTING_WEBHOOK }}
```

### .github/workflows/error-reporting.yml
```diff
@@ -0,0 +1,27 @@
+name: error-reporting
+
+on:
+  workflow_call:
+    secrets:
+      WEBHOOK:
+        required: true
+
+jobs:
+  slack:
+    runs-on: ubuntu-20.04
+    steps:
+      - env:
+          COMMIT_MESSAGE: ${{ github.event.head_commit.message }}
+          COMMIT_AUTHOR_NAME: ${{ github.event.head_commit.author.name }}
+        run: |
+          curl -H "Content-Type: application/json" \
+            -X POST ${{ secrets.WEBHOOK }} \
+            -d '{
+              "attachments": [
+                {
+                  "color": "#AC514C",
+                  "text":
+                    "*${{ github.repository }} (${{ github.workflow }})*\n'"$COMMIT_MESSAGE"' - _'"$COMMIT_AUTHOR_NAME"'_\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Build>",
+                }
+              ]
+            }'
```

### .github/workflows/export-github-repo.yml
```diff
@@ -30,18 +30,6 @@ jobs:
     needs:
       - web3
     if: failure() && github.event_name == 'push'
-    runs-on: ubuntu-20.04
-    steps:
-      - name: Slack
-        run: |
-          curl -H "Content-Type: application/json" \
-            -X POST ${{ secrets.SLACK_ERROR_REPORTING_WEBHOOK }} \
-            -d '{
-              "attachments": [
-                {
-                  "color": "#AC514C",
-                  "text":
-                    "*${{ github.repository }} (${{ github.workflow }})*\n${{ github.event.head_commit.message }} - _${{ github.event.head_commit.author.name }}_\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Build>",
-                }
-              ]
-            }'
+    uses: ./.github/workflows/error-reporting.yml
+    secrets:
+      WEBHOOK: ${{ secrets.SLACK_ERROR_REPORTING_WEBHOOK }}
```

### .github/workflows/release-artifacts-auto.yml
```diff
@@ -22,18 +22,6 @@ jobs:
     needs:
       - release-artifacts
     if: failure() && github.event_name == 'push'
-    runs-on: ubuntu-20.04
-    steps:
-      - name: Slack
-        run: |
-          curl -H "Content-Type: application/json" \
-            -X POST ${{ secrets.SLACK_ERROR_REPORTING_WEBHOOK }} \
-            -d '{
-              "attachments": [
-                {
-                  "color": "#AC514C",
-                  "text":
-                    "*${{ github.repository }} (${{ github.workflow }})*\n${{ github.event.head_commit.message }} - _${{ github.event.head_commit.author.name }}_\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Build>",
-                }
-              ]
-            }'
+    uses: ./.github/workflows/error-reporting.yml
+    secrets:
+      WEBHOOK: ${{ secrets.SLACK_ERROR_REPORTING_WEBHOOK }}
```
