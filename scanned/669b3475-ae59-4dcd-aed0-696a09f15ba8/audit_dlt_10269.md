# [?] ci: Fix failing when vulnerabilities

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-07-17
Source: https://github.com/radixdlt/babylon-node/commit/861014b6748d096f26b190c93fd76e098aea1c04
Type: security-commit

## Details
ci: Fix failing when vulnerabilities

## Patch
### .github/workflows/phylum-daily-analysis.yaml
```diff
@@ -33,13 +33,13 @@ jobs:
               .map(branch => branch.name)
               .filter(name => name === 'DO-2628' || name.startsWith('release/'));
             console.log("Branches name: " + branchNames)
-            return branchNames;
+            return JSON.stringify(branchNames);
           result-encoding: string
 
       - name: Set branches matrix
         id: set_matrix
         run: |
-          echo "branches=$(jq -n --argjson branches "${{ steps.get_branches.outputs.result }}" '{"branches": $branches}') >> $GITHUB_ENV"
+          echo "::set-output name=branches::${{ steps.get_branches.outputs.result }}"
 
   analyze_branch_phylum:
     name: Analyze dependencies with Phylum
```
