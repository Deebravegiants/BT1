# [?] ci: Fix failing when vulnerabilities

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-07-17
Source: https://github.com/radixdlt/babylon-node/commit/d7745f1437955198cc688063001d6a8efc74c1e5
Type: security-commit

## Details
ci: Fix failing when vulnerabilities

## Patch
### .github/workflows/phylum-daily-analysis.yaml
```diff
@@ -8,21 +8,45 @@ on:
     branches:
       - DO-2628
 jobs:
-  phylum_analyze:
+  get_phylum_branches_to_analyze:
+    name: Get Branches to analyze with phylum
+    permissions:
+      contents: read
+      pull-requests: write
+    runs-on: ubuntu-latest
+    steps:
+      - name: Checkout repository
+        uses: RDXWorks-actions/checkout@main
+        with:
+          fetch-depth: 0
+
+      - name: Get branches
+        id: get_branches
+        uses: RDXWorks-actions/github-script@main
+        with:
+          script: |
+            const branches = await github.repos.listBranches({
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+            });
+            const branchNames = branches.data
+              .map(branch => branch.name)
+              .filter(name => name === 'DO-2628' || name.startsWith('release/'));
+            return branchNames;
+          result-encoding: string
+
+      - name: Set branches matrix
+        id: set_matrix
+        run: |
+          echo "branches=$(jq -n --argjson branches "${{ steps.get_branches.outputs.result }}" '{"branches": $branches}') >> $GITHUB_ENV"
+  analyze_branch_phylum:
     name: Analyze dependencies with Phylum
     permissions:
       contents: read
       pull-requests: write
     runs-on: ubuntu-latest
     strategy:
-      matrix:
-        branch: [DO-2628]
-        include:
-          # - branch: main
-          # - branch: develop
-          - branch: DO-2628
-          # - branch: release/*
-
+      matrix: ${{ fromJson(needs.get_phylum_branches_to_analyze.outputs.branches) }}
     steps:
       - uses: RDXWorks-actions/checkout@main
         with:
```
