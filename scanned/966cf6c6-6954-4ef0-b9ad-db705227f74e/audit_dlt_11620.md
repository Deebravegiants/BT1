# [?] Problem: hard to track new dependency vulnerabilities in PR changes (#92)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/chain-main
Published: 2020-09-21
Source: https://github.com/crypto-org-chain/chain-main/commit/e4621746ee1abf2eeb56bcf4469b347f8ae3d34c
Type: security-commit

## Details
Problem: hard to track new dependency vulnerabilities in PR changes (#92)

Solution: temporarily listed out the current ones to be excluded in the GH action

## Patch
### .github/workflows/audit.yml
```diff
@@ -16,4 +16,7 @@ jobs:
     - name: WriteGoList
       run: go list -json -m all > go.list
     - name: Nancy
-      uses: sonatype-nexus-community/nancy-github-action@master
\ No newline at end of file
+      uses: sonatype-nexus-community/nancy-github-action@master
+      # FIXME: https://github.com/crypto-com/chain-main/issues/25 remove exclusion when viper+tendermint are upgraded
+      with:
+        nancyCommand: sleuth --exclude-vulnerability CVE-2018-17848,CVE-2018-17846,CVE-2018-17847,CVE-2018-17142,CVE-2018-17143,CVE-2020-15115,CVE-2020-15136,CVE-2020-15114
\ No newline at end of file
```
