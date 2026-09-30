# [?] feat(ci): Golang dependency vulnerability check (#1138)

## Summary
Severity: Unknown
Chain: Evmos
Component: evmos/evmos
Published: 2022-12-02
Source: https://github.com/evmos/evmos/commit/2b55b3204b9e4286c5070dce2594b741bcb6135a
Type: security-commit

## Details
feat(ci): Golang dependency vulnerability check (#1138)

* fix(app): register node service

* feat(ci): Golang dependency vulnerability check

* c++

## Patch
### .github/workflows/dependencies.yml
```diff
@@ -0,0 +1,28 @@
+name: "Dependency Review"
+on: pull_request
+
+permissions:
+  contents: read
+
+jobs:
+  dependency-review:
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/setup-go@v3
+        with:
+          go-version: 1.19
+          check-latest: true
+      - name: "Checkout Repository"
+        uses: actions/checkout@v3
+      - uses: technote-space/get-diff-action@v6.1.1
+        with:
+          PATTERNS: |
+            **/**.go
+            go.mod
+            go.sum
+      - name: "Dependency Review"
+        uses: actions/dependency-review-action@v3
+        if: env.GIT_DIFF
+      - name: "Go vulnerability check"
+        run: make vulncheck
+        if: env.GIT_DIFF
```

### CHANGELOG.md
```diff
@@ -50,6 +50,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Features
 
+- (ci) [#1138](https://github.com/evmos/evmos/pull/1138) Add Golang dependency vulnerability checker.
 - (app) [\#1114](https://github.com/evmos/evmos/pull/1114) Set default File store listener for application from [ADR38](https://docs.cosmos.network/v0.47/architecture/adr-038-state-listening)
 
 ### Improvements
```

### Makefile
```diff
@@ -168,7 +168,7 @@ clean:
 
 all: build
 
-build-all: tools build lint test
+build-all: tools build lint test vulncheck
 
 .PHONY: distclean clean build-all
 
@@ -270,6 +270,10 @@ go.sum: go.mod
 	go mod verify
 	go mod tidy
 
+vulncheck: $(BUILDDIR)/
+	GOBIN=$(BUILDDIR) go install golang.org/x/vuln/cmd/govulncheck@latest
+	$(BUILDDIR)/govulncheck ./...
+
 ###############################################################################
 ###                              Documentation                              ###
 ###############################################################################
```
