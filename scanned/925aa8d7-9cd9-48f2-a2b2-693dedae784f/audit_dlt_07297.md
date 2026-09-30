# [?] [TransactionResult] Avoid panicing if original column had duplicate entries (#7835)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2022-10-14
Source: https://github.com/near/nearcore/commit/b035277e9e415a82498b13f638f70858ebe602c7
Type: security-commit

## Details
[TransactionResult] Avoid panicing if original column had duplicate entries (#7835)

https://near.zulipchat.com/#narrow/stream/295558-pagoda.2Fcore/topic/DB.20migrate_32_to_33.20panics

That's the only reason I could think of.

## Patch
### core/store/src/migrations.rs
```diff
@@ -246,7 +246,12 @@ pub fn migrate_32_to_33(storage: &crate::NodeStorage) -> anyhow::Result<()> {
     for row in
         store.iter_prefix_ser::<Vec<ExecutionOutcomeWithIdAndProof>>(DBCol::_TransactionResult, &[])
     {
-        let (_, outcomes) = row?;
+        let (_, mut outcomes) = row?;
+        // It appears that it was possible that the same entry in the original column contained
+        // duplicate outcomes. We remove them here to avoid panicing due to issuing a
+        // self-overwriting transaction.
+        outcomes.sort_by_key(|outcome| outcome.id().clone());
+        outcomes.dedup_by_key(|outcome| outcome.id().clone());
         for outcome in outcomes {
             update.insert_ser(
                 DBCol::TransactionResultForBlock,
```
