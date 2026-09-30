# [?] Fix circuits integration tests panic: "unwrap on None value" when EIP-4896 withdrawals==None (#1688)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2023-11-27
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/e39d55cf84a81ad3f42fd7f57fdb978165717926
Type: security-commit

## Details
Fix circuits integration tests panic: "unwrap on None value" when EIP-4896 withdrawals==None (#1688)

### Description

Integration Tests have been failing since introduction of
https://github.com/privacy-scaling-explorations/zkevm-circuits/issues/1369,
due to Option::Unwrap on None value, when eth_block.withdrawals==None.

### Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing
functionality to not work as expected)
- [ ] This change requires a documentation update

### Contents

- zkevm-circuits/zkevm-circuits/src/witness/block.rs

### Rationale
replace eth_block.withdrawals.clone().unwrap() with
eth_block.withdrawals.clone().unwrap_or_default()

### How Has This Been Tested?

https://github.com/privacy-scaling-explorations/zkevm-circuits/actions/runs/6968928576/job/18963801769
<hr>

### Issue

https://github.com/privacy-scaling-explorations/zkevm-circuits/issues/1687

## Patch
### zkevm-circuits/src/witness/block.rs
```diff
@@ -78,7 +78,7 @@ impl<F: Field> Block<F> {
 
     /// Return the list of withdrawals of this block.
     pub fn withdrawals(&self) -> Vec<Withdrawal> {
-        let eth_withdrawals = self.eth_block.withdrawals.clone().unwrap();
+        let eth_withdrawals = self.eth_block.withdrawals.clone().unwrap_or_default();
         eth_withdrawals
             .iter()
             .map({
```
