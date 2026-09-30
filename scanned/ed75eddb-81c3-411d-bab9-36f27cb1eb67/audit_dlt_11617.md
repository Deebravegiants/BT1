# [?] Problem: known vulnerabilities according to Go Nancy's scan (fixes #784) (#858)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/chain-main
Published: 2022-09-08
Source: https://github.com/crypto-org-chain/chain-main/commit/41d104a51991af73223a800eccd255bbf6e932ce
Type: security-commit

## Details
Problem: known vulnerabilities according to Go Nancy's scan (fixes #784) (#858)

Solution: replaced Go Nancy with govulncheck that checks based
on transitively called functions (ref: https://go.dev/blog/vuln )

## Patch
### .github/workflows/audit.yml
```diff
@@ -1,4 +1,4 @@
-name: Go Nancy
+name: govuln
 
 on:
     pull_request:
@@ -7,20 +7,19 @@ on:
         - master
         - release/**
 jobs:
-  build:
+  check:
 
     runs-on: ubuntu-latest
 
     steps:
+    - name: Set up Go
+      uses: actions/setup-go@v3
+      with:
+        go-version: 1.19.1
     - uses: actions/checkout@v2
       with:
           submodules: true
-    - name: WriteGoList
-      run: go list -json -m all > go.list
-    - name: Nancy
-      uses: sonatype-nexus-community/nancy-github-action@main
-      # FIXME: https://github.com/crypto-com/chain-main/issues/25 remove exclusion when viper+tendermint are upgraded
-      # FIXME(CVE-2022-23327): github.com/coinbase/rosetta-sdk-go contains a vulnerable version of go-ethereum. Remove this when it is updated in upstream.
-      #                        (https://ossindex.sonatype.org/vulnerability/de9d3742-ac18-44af-bebb-5727e3957c94?component-type=golang&component-name=github.com/ethereum/go-ethereum&utm_source=nancy-client&utm_medium=integration&utm_content=0.0.0-dev)
-      with:
-        nancyCommand: sleuth --exclude-vulnerability CVE-2020-15115,CVE-2020-15136,CVE-2021-41173,CVE-2020-15114,CVE-2022-23327
+    - name: install govulncheck
+      run: go install golang.org/x/vuln/cmd/govulncheck@latest
+    - name: govuln sec scan
+      run: govulncheck ./...
```
