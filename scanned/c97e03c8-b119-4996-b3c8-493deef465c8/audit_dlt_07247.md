# [?] build: Makefile: add Go vulnerability checker (#14028)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2022-12-02
Source: https://github.com/cosmos/cosmos-sdk/commit/bcfb7dc330f2255bf0f699579531c4e995a94129
Type: security-commit

## Details
build: Makefile: add Go vulnerability checker (#14028)

* build: Makefile: add Go vulnerability checker

Adds the Go vulnerability checker to the Makefile as a directive
dependency to the all directive to ensure that we get security
updates scalably.

* add gh action

* bump to 1.19.3 due to vulnerabilities

Co-authored-by: Julien Robert <julien@rbrt.fr>

## Patch
### .github/workflows/build.yml
```diff
@@ -23,7 +23,7 @@ jobs:
       - uses: actions/checkout@v3
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: technote-space/get-diff-action@v6.1.1
         id: git_diff
         with:
```

### .github/workflows/codeql-analysis.yml
```diff
@@ -25,7 +25,7 @@ jobs:
         uses: actions/checkout@v3
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       # Initializes the CodeQL tools for scanning.
       - name: Initialize CodeQL
         uses: github/codeql-action/init@v2
```

### .github/workflows/cosmovisor-release.yml
```diff
@@ -18,7 +18,7 @@ jobs:
           fetch-depth: 0
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       # get 'v*.*.*' part from 'cosmovisor/v*.*.*' and save to $GITHUB_ENV
       - name: Set env
         run: echo "RELEASE_VERSION=${GITHUB_REF#refs/*/cosmovisor/}" >> $GITHUB_ENV
```

### .github/workflows/dependabot-update-all.yml
```diff
@@ -17,7 +17,7 @@ jobs:
           token: ${{ secrets.PRBOT_PAT }}
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - name: Extract updated dependency
         id: deps
         run: |
```

### .github/workflows/dependencies-review.yml
```diff
@@ -10,10 +10,12 @@ jobs:
     steps:
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - name: "Checkout Repository"
         uses: actions/checkout@v3
       - name: "Dependency Review"
         uses: actions/dependency-review-action@v3
       - name: "Dependency audit"
         run: ./scripts/dep-assert.sh
+      - name: "Go vulnerability check"
+        run: make vulncheck
```

### .github/workflows/lint.yml
```diff
@@ -17,7 +17,7 @@ jobs:
       - uses: actions/setup-go@v3
         with:
           # ci is set to go1.19 to match developer setups
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/checkout@v3
       - name: golangci-lint
         uses: golangci/golangci-lint-action@v3
```

### .github/workflows/release.yml
```diff
@@ -20,7 +20,7 @@ jobs:
       - name: Install Go
         uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - name: Unshallow
         run: git fetch --prune --unshallow
       - name: Create release
```

### .github/workflows/sims-045.yml
```diff
@@ -21,7 +21,7 @@ jobs:
           ref: "release/v0.45.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - run: make build
 
   install-runsim:
@@ -32,7 +32,7 @@ jobs:
     steps:
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - name: Install runsim
         run: go install github.com/cosmos/tools/cmd/runsim@v1.0.0
       - uses: actions/cache@v3
@@ -49,7 +49,7 @@ jobs:
           ref: "release/v0.45.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
@@ -67,7 +67,7 @@ jobs:
           ref: "release/v0.45.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
@@ -86,7 +86,7 @@ jobs:
           ref: "release/v0.45.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
```

### .github/workflows/sims-046.yml
```diff
@@ -21,7 +21,7 @@ jobs:
           ref: "release/v0.46.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - run: make build
 
   install-runsim:
@@ -32,7 +32,7 @@ jobs:
     steps:
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - name: Install runsim
         run: go install github.com/cosmos/tools/cmd/runsim@v1.0.0
       - uses: actions/cache@v3
@@ -50,7 +50,7 @@ jobs:
           ref: "release/v0.46.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
@@ -68,7 +68,7 @@ jobs:
           ref: "release/v0.46.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
@@ -86,7 +86,7 @@ jobs:
           ref: "release/v0.46.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
```

### .github/workflows/sims-047.yml
```diff
@@ -21,7 +21,7 @@ jobs:
           ref: "release/v0.47.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - run: make build
 
   install-runsim:
@@ -32,7 +32,7 @@ jobs:
     steps:
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - name: Install runsim
         run: go install github.com/cosmos/tools/cmd/runsim@v1.0.0
       - uses: actions/cache@v3
@@ -50,7 +50,7 @@ jobs:
           ref: "release/v0.47.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
@@ -68,7 +68,7 @@ jobs:
           ref: "release/v0.47.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
@@ -86,7 +86,7 @@ jobs:
           ref: "release/v0.47.x"
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
```

### .github/workflows/sims-nightly.yml
```diff
@@ -22,7 +22,7 @@ jobs:
     steps:
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - name: Install runsim
         run: go install github.com/cosmos/tools/cmd/runsim@v1.0.0
       - uses: actions/cache@v3
@@ -36,7 +36,7 @@ jobs:
       - uses: actions/checkout@v3
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
```

### .github/workflows/sims.yml
```diff
@@ -21,7 +21,7 @@ jobs:
       - uses: actions/checkout@v3
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - run: make build
       - name: Install runsim
         run: go install github.com/cosmos/tools/cmd/runsim@v1.0.0
@@ -38,7 +38,7 @@ jobs:
       - uses: actions/checkout@v3
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
@@ -54,7 +54,7 @@ jobs:
       - uses: actions/checkout@v3
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
@@ -71,7 +71,7 @@ jobs:
       - uses: actions/checkout@v3
       - uses: actions/setup-go@v3
         with:
-          go-version: 1.19.2
+          go-version: 1.19.3
       - uses: actions/cache@v3
         with:
           path: ~/go/bin
```
