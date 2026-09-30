# [?] ci: Fix failing when vulnerabilities

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-07-17
Source: https://github.com/radixdlt/babylon-node/commit/af5d3fe4cb95546568f2e6d40e88aa235849529d
Type: security-commit

## Details
ci: Fix failing when vulnerabilities

## Patch
### .github/workflows/phylum-daily-analysis.yaml
```diff
@@ -25,7 +25,7 @@ jobs:
         uses: RDXWorks-actions/github-script@main
         with:
           script: |
-            const branches = await github.repos.listBranches({
+            const branches = await github.rest.repos.listBranches({
               owner: context.repo.owner,
               repo: context.repo.repo,
             });
```
