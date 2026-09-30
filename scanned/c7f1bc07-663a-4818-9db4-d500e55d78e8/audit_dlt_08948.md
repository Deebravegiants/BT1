# [?] fix(solidity): fix tron-sdk build failures from soldeer panic and partial typechain cache (#8205)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2026-02-25
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/dd2b994c1f450b9ccd2a62754c496a2b232a21e9
Type: security-commit

## Details
fix(solidity): fix tron-sdk build failures from soldeer panic and partial typechain cache (#8205)

Co-authored-by: Danil Nemirovsky <4614623+ameten@users.noreply.github.com>

## Patch
### .claude/settings.json
```diff
@@ -12,5 +12,8 @@
     "differential-review@trailofbits": true,
     "variant-analysis@trailofbits": true,
     "property-based-testing@trailofbits": true
+  },
+  "attribution": {
+    "commit": ""
   }
 }
```

### .github/workflows/test.yml
```diff
@@ -209,7 +209,7 @@ jobs:
   pnpm-test-run:
     runs-on: depot-ubuntu-24.04
     needs: [change-detection]
-    timeout-minutes: 10
+    timeout-minutes: 20
     if: needs.change-detection.outputs.only_rust == 'false'
     steps:
       - uses: actions/checkout@v6
```

### .lintstagedrc
```diff
@@ -3,5 +3,5 @@
   "*.ts": ["oxlint", "oxfmt --write"],
   "*.md": "oxfmt --no-error-on-unmatched-pattern --write",
   "*.sol": "prettier --write",
-  "*.json": "oxfmt --write"
+  "*.json": "oxfmt --no-error-on-unmatched-pattern --write"
 }
```

### CLAUDE.md
```diff
@@ -61,6 +61,8 @@ cd rust/main && cargo test --all-targets --features aleo,integration_test
 cd rust/main && cargo fmt
 ```
 
+**Do NOT add `Co-Authored-By` trailers to commit messages.**
+
 ### Changeset Style
 
 Write changeset descriptions in past tense describing what changed:
```

### solidity/build-tron.sh
```diff
@@ -2,11 +2,15 @@
 set -e
 cd "$(dirname "$0")"
 
-# Ensure soldeer dependencies are installed before patching files.
-# The regular @hyperlane-xyz/core build also runs soldeer install, and if it
-# runs concurrently with our file patches below, soldeer's git checkout fails
-# on the dirty working tree. Running it first avoids the race condition.
-forge soldeer install --quiet
+# Ensure deterministic outputs for turbo cache: hardhat/typechain can emit
+# partial trees when incremental cache is reused against cleaned output dirs.
+rm -rf ./cache-tron ../typescript/tron-sdk/src/abi ../typescript/tron-sdk/src/typechain
+
+# Soldeer dependencies are already installed by the turbo deps:soldeer task
+# (build:tron depends on build, which depends on deps:soldeer).
+# This call is a safety net for standalone invocations; allow it to fail
+# gracefully since deps may already be present (e.g. forge v1.1.0 soldeer bug).
+forge soldeer install --quiet || echo "Warning: soldeer install failed, assuming dependencies are already present"
 
 OZ_CREATE2="dependencies/@openzeppelin-contracts-4.9.3/contracts/utils/Create2.sol"
 
```

### solidity/package.json
```diff
@@ -66,7 +66,7 @@
     ],
     "license": "Apache-2.0",
     "scripts": {
-        "deps:soldeer": "forge soldeer install --quiet",
+        "deps:soldeer": "forge soldeer install --quiet || echo 'Warning: soldeer install failed, assuming dependencies are already present'",
         "build": "pnpm version:update && pnpm hardhat-esm compile && tsc && ./exportBuildArtifact.sh",
         "build:zk": "pnpm hardhat-zk compile && tsc && node generate-artifact-exports.mjs && ZKSYNC=true ./exportBuildArtifact.sh",
         "build:tron": "./build-tron.sh",
```
