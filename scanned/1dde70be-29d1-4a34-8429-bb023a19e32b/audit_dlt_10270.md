# [?] ci: Fix failing when vulnerabilities

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-07-17
Source: https://github.com/radixdlt/babylon-node/commit/04923b1dea201e7dbbadce066fac592236cdb0cb
Type: security-commit

## Details
ci: Fix failing when vulnerabilities

## Patch
### .github/workflows/phylum-daily-analysis.yaml
```diff
@@ -32,13 +32,15 @@ jobs:
             const branchNames = branches.data
               .map(branch => branch.name)
               .filter(name => name === 'DO-2628' || name.startsWith('release/'));
+            console.log("Branches name: " + branchNames)
             return branchNames;
           result-encoding: string
 
       - name: Set branches matrix
         id: set_matrix
         run: |
           echo "branches=$(jq -n --argjson branches "${{ steps.get_branches.outputs.result }}" '{"branches": $branches}') >> $GITHUB_ENV"
+
   analyze_branch_phylum:
     name: Analyze dependencies with Phylum
     permissions:
```
