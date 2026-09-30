# [?] Run vulnerability scan on latest release tags

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2025-02-14
Source: https://github.com/hyperledger/fabric/commit/f07477bb8b48f387c5d7dd15361c4df99f521da4
Type: security-commit

## Details
Run vulnerability scan on latest release tags

Vulnerability scans were previously run only on the latest state of
currently developed branches. This provided assurance that the current
branch state did not contain known vulnerabilities in dependencies, but
did not provide assurance that the currently released code was free of
vulnerabilities.

This change runs additional vulnerability scans on the most recent
release version tag for currently developed branches. Scan failures now
indicate that a new release is required to address vulnerabilities in
dependencies.

Signed-off-by: Mark S. Lewis <Mark.S.Lewis@outlook.com>

## Patch
### .github/workflows/vulnerability-scan.yml
```diff
@@ -13,7 +13,7 @@ permissions:
   contents: read
 
 jobs:
-  scan:
+  latest:
     # Only run the scheduled job in hyperledger/fabric repository, not on personal forks
     if: github.event_name != 'schedule' || (github.event_name == 'schedule' && github.repository == 'hyperledger/fabric')
     runs-on: ${{ github.repository == 'hyperledger/fabric' && 'fabric-ubuntu-22.04' || 'ubuntu-22.04' }}
@@ -24,12 +24,43 @@ jobs:
           - main
           - release-2.5
     steps:
-      - uses: actions/checkout@v4
+      - name: Checkout ${{ matrix.ref }} branch
+        uses: actions/checkout@v4
         with:
           ref: ${{ matrix.ref }}
       - name: Set up Go
         uses: actions/setup-go@v5
         with:
           go-version: 1.24.0
       - name: Scan
-        run: make scan
+        run: go run github.com/google/osv-scanner/cmd/osv-scanner@b37c83e19af3b2555864457cbd0b08ef0e1f9d7d scan --lockfile=go.mod || (( $? > 1 && $? < 127 ))
+
+  release:
+    # Only run the scheduled job in hyperledger/fabric repository, not on personal forks
+    if: github.event_name != 'schedule' || (github.event_name == 'schedule' && github.repository == 'hyperledger/fabric')
+    runs-on: ${{ github.repository == 'hyperledger/fabric' && 'fabric-ubuntu-22.04' || 'ubuntu-22.04' }}
+    strategy:
+      fail-fast: false
+      matrix:
+        ref:
+          - main
+          - release-2.5
+    steps:
+      - name: Checkout ${{ matrix.ref }} branch
+        uses: actions/checkout@v4
+        with:
+          ref: ${{ matrix.ref }}
+          fetch-depth: 0
+      - name: Get latest release tag
+        id: latest-release
+        run: echo "tag=$(git -c versionsort.suffix=- tag --merged HEAD --sort=-version:refname | head -1)" >> "${GITHUB_OUTPUT}"
+      - name: Checkout ${{ steps.latest-release.outputs.tag }}
+        uses: actions/checkout@v4
+        with:
+          ref: ${{ steps.latest-release.outputs.tag }}
+      - name: Set up Go
+        uses: actions/setup-go@v5
+        with:
+          go-version: 1.24.0
+      - name: Scan
+        run: go run github.com/google/osv-scanner/cmd/osv-scanner@b37c83e19af3b2555864457cbd0b08ef0e1f9d7d scan --lockfile=go.mod || (( $? > 1 && $? < 127 ))
```

### Makefile
```diff
@@ -106,19 +106,19 @@ help: ## List all commands with documentation
 	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
 
 .PHONY: all
-all: ## Builds all targets and runs all non-integration tests/checks 
+all: ## Builds all targets and runs all non-integration tests/checks
 	check-go-version native docker checks
 
 .PHONY: checks
-checks: ## Runs basic checks along with unit and integration tests 
+checks: ## Runs basic checks along with unit and integration tests
 	basic-checks unit-test integration-test
 
 .PHONY: basic-checks
-basic-checks: check-go-version license spelling references trailing-spaces linter check-help-docs check-metrics-doc filename-spaces check-swagger ## Performs basic checks like license, spelling, trailing spaces and linter 
+basic-checks: check-go-version license spelling references trailing-spaces linter check-help-docs check-metrics-doc filename-spaces check-swagger ## Performs basic checks like license, spelling, trailing spaces and linter
 
 
 .PHONY: desk-checks
-desk-check: ## Runs linters and verify to test changed packages 
+desk-check: ## Runs linters and verify to test changed packages
 	checks verify
 
 .PHONY: help-docs
@@ -344,7 +344,7 @@ release-clean: $(RELEASE_PLATFORMS:%=%-release-clean) ## Clean release packages
 	-@rm -rf release/$*
 
 .PHONY: unit-test-clean
-unit-test-clean: 
+unit-test-clean:
 
 .PHONY: filename-spaces
 spaces: # Check for spaces in file names
@@ -372,8 +372,8 @@ ccaasbuilder/%: ccaasbuilder-clean
 ccaasbuilder: ccaasbuilder/$(MARCH)
 
 .PHONY: scan
-scan: scan-govulncheck ## Run all security scans
+scan: scan-osv-scanner ## Run all vulnerability scans
 
-.PHONY: scan-govulncheck
-scan-govulncheck: gotool.govulncheck ## Run gosec security scan
-	govulncheck ./...
+.PHONY: scan-osv-scanner ## Run OSV-Scanner vulnerability scan
+scan-osv-scanner:
+	go run github.com/google/osv-scanner/cmd/osv-scanner@b37c83e19af3b2555864457cbd0b08ef0e1f9d7d scan --lockfile=go.mod || [ \( $$? -gt 1 \) -a \( $$? -lt 127 \) ]
```

### gotools.mk
```diff
@@ -16,7 +16,6 @@ go.fqp.gocov-xml          := github.com/AlekSi/gocov-xml
 go.fqp.gofumpt            := mvdan.cc/gofumpt
 go.fqp.goimports          := golang.org/x/tools/cmd/goimports
 go.fqp.golint             := golang.org/x/lint/golint
-go.fqp.govulncheck        := golang.org/x/vuln/cmd/govulncheck@latest
 go.fqp.misspell           := github.com/client9/misspell/cmd/misspell
 go.fqp.mockery            := github.com/vektra/mockery/v2
 go.fqp.protoc-gen-go      := google.golang.org/protobuf/cmd/protoc-gen-go
```
