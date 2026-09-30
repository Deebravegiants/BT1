# [?] fix: race condition in goreleaser workflow (#15233)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-11-13
Source: https://github.com/smartcontractkit/chainlink/commit/f9f9079d2d7e3b8eece0bfb07b3eec5b99c3ff09
Type: security-commit

## Details
fix: race condition in goreleaser workflow (#15233)

* fix: race condition in goreleaser workflow

* fix: typos

## Patch
### .github/workflows/build-publish-develop-pr.yml
```diff
@@ -24,7 +24,10 @@ on:
         default: "false"
 
 env:
-  GIT_REF: ${{ github.event.inputs.git_ref || github.ref }}
+  # Use github.sha here otherwise a race condition exists if
+  # a commit is pushed to develop before merge is run.
+  CHECKOUT_REF: ${{ github.event.inputs.git_ref || github.sha }}
+
 
 jobs:
   merge:
@@ -38,7 +41,7 @@ jobs:
       - name: Checkout repository
         uses: actions/checkout@v4.2.1
         with:
-          ref: ${{ env.GIT_REF }}
+          ref: ${{ env.CHECKOUT_REF }}
 
       - name: Configure aws credentials
         uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502 # v4.0.2
@@ -48,13 +51,13 @@ jobs:
           mask-aws-account-id: true
           role-session-name: "merge"
 
-      - uses: actions/cache/restore@v4
+      - uses: actions/cache/restore@v4.1.1
         with:
           path: dist/linux_amd64_v1
           key: chainlink-amd64-${{ github.sha }}
           fail-on-cache-miss: true
 
-      - uses: actions/cache/restore@v4
+      - uses: actions/cache/restore@v4.1.1
         with:
           path: dist/linux_arm64_v8.0
           key: chainlink-arm64-${{ github.sha }}
@@ -91,7 +94,7 @@ jobs:
       - name: Checkout repository
         uses: actions/checkout@v4.2.1
         with:
-          ref: ${{ env.GIT_REF }}
+          ref: ${{ env.CHECKOUT_REF }}
           fetch-depth: 0
 
       - name: Configure aws credentials
@@ -103,7 +106,7 @@ jobs:
           role-session-name: "split-${{ matrix.goarch }}"
 
       - id: cache
-        uses: actions/cache@v4
+        uses: actions/cache@v4.1.1
         with:
           path: dist/${{ matrix.dist_name }}
           key: chainlink-${{ matrix.goarch }}-${{ github.sha }}
@@ -125,9 +128,9 @@ jobs:
       release-type: ${{ steps.get-image-tag.outputs.release-type }}
     steps:
       - name: Checkout repository
-        uses: actions/checkout@v4
+        uses: actions/checkout@v4.2.1
         with:
-          ref: ${{ env.GIT_REF }}
+          ref: ${{ env.CHECKOUT_REF }}
 
       - name: Get image tag
         id: get-image-tag
```
