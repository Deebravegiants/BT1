# [?] Fix crash in positions --include-closed and display multi-sided LPs consistently (#4583)

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2024-06-11
Source: https://github.com/penumbra-zone/penumbra/commit/a4bede1c5d6d227625fa551790e62b73f5640341
Type: security-commit

## Details
Fix crash in positions --include-closed and display multi-sided LPs consistently (#4583)

## Patch
### crates/bin/pcli/src/command/utils.rs
```diff
@@ -85,7 +85,8 @@ pub(crate) fn render_positions(asset_cache: &asset::Cache, positions: &[Position
                     .format(asset_cache),
                 ]);
                 table.add_row(vec![
-                    String::new(),
+                    // Add a mark indicating this row is associated with the same position.
+                    "└──────────────────────────────────────────────────────────────▶".to_string(),
                     String::new(),
                     format!("{}bps", position.phi.component.fee),
                     format!("Unknown asset"),
```

### crates/core/component/dex/src/lp/order.rs
```diff
@@ -200,6 +200,10 @@ impl SellOrder {
         let desired_amount = U128x128::from(self.desired.amount);
         let offered_unit_amount = U128x128::from(offered_unit.unit_amount());
 
+        if offered_amount == 0u64.into() {
+            return Ok("∞".to_string());
+        }
+
         let price_amount: Amount = ((desired_amount * offered_unit_amount) / offered_amount)?
             // TODO: Is this the correct rounding behavior? Should we expect this to round-trip exactly?
             .round_up()?
```
