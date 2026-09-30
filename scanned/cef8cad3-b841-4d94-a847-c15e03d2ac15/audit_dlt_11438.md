# [?] CCIP-2642: Fixing panic in regex parsing (#1105)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-06-26
Source: https://github.com/smartcontractkit/ccip/commit/a5218b359c9f99f4d7bfe47fa8ae2587a9855245
Type: security-commit

## Details
CCIP-2642: Fixing panic in regex parsing (#1105)

## Motivation
Post test result to slack job panics while parsing the github job name.

https://github.com/smartcontractkit/ccip/actions/runs/9670389604/job/26679921641

## Solution
Fix the regex per
[golang/re2](https://github.com/google/re2/wiki/Syntax) syntax and
remove the matrix which is not needed as we have only one thing to deal.

Sample successful run:
https://github.com/smartcontractkit/ccip/actions/runs/9683107526/job/26717788969

## Patch
### .github/workflows/ccip-load-tests.yml
```diff
@@ -258,7 +258,7 @@ jobs:
           SLACK_BOT_TOKEN: ${{ secrets.QA_SLACK_API_KEY }}
 
   post-test-results-to-slack:
-    name: Post Test Results for ${{ matrix.network }}
+    name: Post Test Results
     if: ${{ failure() && needs.start-slack-thread.result != 'skipped' && needs.start-slack-thread.result != 'cancelled' }}
     environment: integration
     permissions:
@@ -268,10 +268,6 @@ jobs:
       contents: read
     runs-on: ubuntu-latest
     needs: start-slack-thread
-    strategy:
-      fail-fast: false
-      matrix:
-        network: [CCIP]
     steps:
       - name: Checkout the repo
         uses: actions/checkout@9bb56186c3b09b4f86b1c65136769dd318469633 # v4.1.2
@@ -283,8 +279,8 @@ jobs:
           github_token: ${{ github.token }}
           github_repository: ${{ github.repository }}
           workflow_run_id: ${{ github.run_id }}
-          github_job_name_regex: ^${{ matrix.network }} (.*?)$
-          message_title: ${{ matrix.network }}
+          github_job_name_regex: ^CCIP (.*)$
+          message_title: CCIP Jobs
           slack_channel_id: "#ccip-testing"
           slack_bot_token: ${{ secrets.QA_SLACK_API_KEY }}
           slack_thread_ts: ${{ needs.start-slack-thread.outputs.thread_ts }}
```
