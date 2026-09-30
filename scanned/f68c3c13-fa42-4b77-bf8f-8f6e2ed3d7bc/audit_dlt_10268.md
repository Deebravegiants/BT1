# [?] ci: Fix failing when vulnerabilities

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-07-17
Source: https://github.com/radixdlt/babylon-node/commit/0c92468748e5d8439d67c4d76e7ad5ed344d29c9
Type: security-commit

## Details
ci: Fix failing when vulnerabilities

## Patch
### .github/workflows/phylum-daily-analysis.yaml
```diff
@@ -29,6 +29,9 @@ jobs:
               owner: context.repo.owner,
               repo: context.repo.repo,
             });
+            const initBranchesNames = branches.data
+              .map(branch => branch.name)
+            console.log("InitBranches name: " + initBranchesNames)
             const branchNames = branches.data
               .map(branch => branch.name)
               .filter(name => name === 'DO-2628' || name.startsWith('release/'));
```
