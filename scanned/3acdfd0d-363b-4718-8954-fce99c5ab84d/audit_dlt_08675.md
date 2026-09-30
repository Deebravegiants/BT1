# [?] tx: prevent overflow in arbitrary masp builder

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-07-16
Source: https://github.com/namada-net/namada/commit/9de44c48aad0c467e8e67a9c5609bd32faa819b7
Type: security-commit

## Details
tx: prevent overflow in arbitrary masp builder

## Patch
### crates/tx/src/types.rs
```diff
@@ -797,8 +797,9 @@ impl arbitrary::Arbitrary<'_> for MaspBuilder {
             fn map_notifier(&self, _s: N1) {}
         }
 
-        let target_height: masp_primitives::consensus::BlockHeight =
-            arbitrary::Arbitrary::arbitrary(u)?;
+        let target_height = masp_primitives::consensus::BlockHeight::from(
+            u.int_in_range(0_u32..=100_000_000)?,
+        );
         Ok(MaspBuilder {
             target: arbitrary::Arbitrary::arbitrary(u)?,
             asset_types: arbitrary::Arbitrary::arbitrary(u)?,
```
