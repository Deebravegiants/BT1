# [?] Fix minor vec access panic opportunity

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2019-09-09
Source: https://github.com/sigp/lighthouse/commit/15220ae56587bf925154d1ed47f02e6124f4a081
Type: security-commit

## Details
Fix minor vec access panic opportunity

## Patch
### eth2/state_processing/src/per_block_processing/signature_sets.rs
```diff
@@ -42,8 +42,12 @@ pub fn block_proposal_signature_set<'a, T: EthSpec>(
     block_signed_root: Option<Hash256>,
     spec: &'a ChainSpec,
 ) -> Result<SignatureSet<'a>> {
-    let block_proposer = &state.validators
-        [state.get_beacon_proposer_index(block.slot, RelativeEpoch::Current, spec)?];
+    let proposer_index =
+        state.get_beacon_proposer_index(block.slot, RelativeEpoch::Current, spec)?;
+    let block_proposer = &state
+        .validators
+        .get(proposer_index)
+        .ok_or_else(|| Error::ValidatorUnknown(proposer_index as u64))?;
 
     let domain = spec.get_domain(
         block.slot.epoch(T::slots_per_epoch()),
```
