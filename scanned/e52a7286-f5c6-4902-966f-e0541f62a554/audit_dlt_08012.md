# [?] fix: set Atomic Batch CI runner to XL to avoid resource exhaustion (#25079)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2026-04-20
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/246ee28aa6861c50782f55337134366f6a9d5e53
Type: security-commit

## Details
fix: set Atomic Batch CI runner to XL to avoid resource exhaustion (#25079)

Signed-off-by: Alex Kehayov <aleks.kehayov@limechain.tech>

## Patch
### .github/workflows/zxc-execute-hapi-tests.yaml
```diff
@@ -937,7 +937,7 @@ jobs:
   hapi-tests-atomic-batch:
     name: "HAPI Tests (Atomic Batch)"
     if: ${{ inputs.enable-hapi-tests-atomic-batch == 'true' }}
-    runs-on: hl-cn-hapi-lin-lg
+    runs-on: hl-cn-hapi-lin-xl
     outputs:
       failure-mode: ${{ steps.set-failure-mode.outputs.failure-mode }}
     steps:
```
