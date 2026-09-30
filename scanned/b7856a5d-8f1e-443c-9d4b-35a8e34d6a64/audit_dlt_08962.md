# [?] Use OSV-Scanner v2 for vulnerability scan

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2025-03-20
Source: https://github.com/hyperledger/fabric/commit/970bad34e1485b0541d1953d3b5353945fc4828f
Type: security-commit

## Details
Use OSV-Scanner v2 for vulnerability scan

Replace use of OSV-Scanner v1 with v2.

Signed-off-by: Mark S. Lewis <Mark.S.Lewis@outlook.com>

## Patch
### .github/workflows/vulnerability-scan.yml
```diff
@@ -33,7 +33,7 @@ jobs:
         with:
           go-version-file: go.mod
       - name: Scan
-        run: go run github.com/google/osv-scanner/cmd/osv-scanner@b37c83e19af3b2555864457cbd0b08ef0e1f9d7d scan --lockfile=go.mod || (( $? > 1 && $? < 127 ))
+        run: go run github.com/google/osv-scanner/v2/cmd/osv-scanner@latest scan --lockfile=go.mod || (( $? > 1 && $? < 127 ))
 
   release:
     # Only run the scheduled job in hyperledger/fabric repository, not on personal forks
@@ -63,4 +63,4 @@ jobs:
         with:
           go-version-file: go.mod
       - name: Scan
-        run: go run github.com/google/osv-scanner/cmd/osv-scanner@b37c83e19af3b2555864457cbd0b08ef0e1f9d7d scan --lockfile=go.mod || (( $? > 1 && $? < 127 ))
+        run: go run github.com/google/osv-scanner/v2/cmd/osv-scanner@latest scan --lockfile=go.mod || (( $? > 1 && $? < 127 ))
```

### Makefile
```diff
@@ -379,4 +379,4 @@ scan: scan-osv-scanner ## Run all vulnerability scans
 
 .PHONY: scan-osv-scanner ## Run OSV-Scanner vulnerability scan
 scan-osv-scanner:
-	go run github.com/google/osv-scanner/cmd/osv-scanner@b37c83e19af3b2555864457cbd0b08ef0e1f9d7d scan --lockfile=go.mod || [ \( $$? -gt 1 \) -a \( $$? -lt 127 \) ]
+	go run github.com/google/osv-scanner/v2/cmd/osv-scanner@latest scan --lockfile=go.mod || [ \( $$? -gt 1 \) -a \( $$? -lt 127 \) ]
```
