# [?] fix: avoid LNv1 gateway fee crash (#9061)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-26
Source: https://github.com/fedimint/fedimint/commit/0f64e0deeb0f4ba52cfc28012d67fe8debe69ec0
Type: security-commit

## Details
fix: avoid LNv1 gateway fee crash (#9061)

Summary

Fix the LNv1 gateway fee crash for pathological proportional fees
without changing the deployed fee calculation for normal rates.

Details

- Makes `RoutingFees::to_amount` handle `proportional_millionths >
1_000_000` without dividing by zero by pricing the fee out of range.
- Saturates the final base-fee addition instead of allowing overflow.
- Rejects gateway registrations above `1_000_000` ppm at the server
boundary.
- Adds regression coverage that keeps the existing divisor-based values,
including `3_000 ppm -> 3_003 msat`, unchanged.

Reviewing

This intentionally does not fix the small LNv1 fee
miscalculation/rounding behavior from #9012. It only addresses the crash
path from #8975.

Testing

- [x] `just format`
- [x] `cargo test -p fedimint-ln-common config::tests`
- [x] `cargo test -p fedimint-ln-server
registration_with_absurd_proportional_fee_is_rejected`
- [x] `cargo clippy -p fedimint-ln-common -p fedimint-ln-server --tests
-- -D warnings`

Fixes #8975

Extracted from discussion on #9012.

## Patch
### modules/fedimint-ln-common/src/config.rs
```diff
@@ -96,13 +96,15 @@ pub trait FeeToAmount {
 impl FeeToAmount for RoutingFees {
     fn to_amount(&self, payment: &Amount) -> Amount {
         let base_fee = u64::from(self.base_msat);
-        let margin_fee: u64 = if self.proportional_millionths > 0 {
-            let fee_percent = 1_000_000 / u64::from(self.proportional_millionths);
-            payment.msats / fee_percent
-        } else {
-            0
+        let margin_fee = match 1_000_000_u64.checked_div(u64::from(self.proportional_millionths)) {
+            None => 0,
+            Some(0) => u64::MAX,
+            Some(fee_percent) => payment.msats / fee_percent,
         };
 
-        msats(base_fee + margin_fee)
+        msats(base_fee.saturating_add(margin_fee))
     }
 }
+
+#[cfg(test)]
+mod tests;
```

### modules/fedimint-ln-common/src/config/tests.rs
```diff
@@ -0,0 +1,56 @@
+use fedimint_core::{Amount, msats};
+use lightning_invoice::RoutingFees;
+
+use super::FeeToAmount;
+
+fn fees(base_msat: u32, proportional_millionths: u32) -> RoutingFees {
+    RoutingFees {
+        base_msat,
+        proportional_millionths,
+    }
+}
+
+/// `LNv1`'s deployed fee formula divides by a truncated divisor. Keep those
+/// values stable while making the pathological divisor non-panicking.
+#[test]
+fn margin_uses_legacy_truncated_divisor() {
+    assert_eq!(fees(0, 100).to_amount(&msats(1_000_000)), msats(100));
+    assert_eq!(fees(0, 3_000).to_amount(&msats(1_000_000)), msats(3_003));
+    assert_eq!(
+        fees(0, 600_000).to_amount(&msats(1_000_000)),
+        msats(1_000_000)
+    );
+    assert_eq!(
+        fees(0, 1_000_000).to_amount(&msats(1_000_000)),
+        msats(1_000_000)
+    );
+}
+
+#[test]
+fn base_fee_is_added_to_the_margin() {
+    assert_eq!(fees(500, 0).to_amount(&msats(1_000_000)), msats(500));
+    assert_eq!(fees(500, 100).to_amount(&msats(1_000_000)), msats(600));
+    assert_eq!(fees(500, 0).to_amount(&Amount::ZERO), msats(500));
+}
+
+/// A rate above one million used to make `1_000_000 / rate` truncate to zero,
+/// and the division by it panicked. Price it out of range instead.
+#[test]
+fn rate_above_one_million_prices_out_of_range_rather_than_panicking() {
+    assert_eq!(
+        fees(0, 1_000_001).to_amount(&msats(1_000_000)),
+        msats(u64::MAX)
+    );
+    assert_eq!(
+        fees(0, u32::MAX).to_amount(&msats(1_000_000)),
+        msats(u64::MAX)
+    );
+}
+
+#[test]
+fn base_fee_addition_saturates() {
+    assert_eq!(
+        fees(u32::MAX, 1_000_000).to_amount(&msats(u64::MAX)),
+        msats(u64::MAX)
+    );
+}
```

### modules/fedimint-ln-server/src/lib.rs
```diff
@@ -1502,6 +1502,12 @@ impl Lightning {
 
         let gateway_id = gateway.info.gateway_id;
 
+        anyhow::ensure!(
+            gateway.info.fees.proportional_millionths <= 1_000_000,
+            "Gateway registration fee of {} proportional millionths exceeds the payment itself",
+            gateway.info.fees.proportional_millionths
+        );
+
         // Reject a forged proof outright rather than silently downgrading it to an
         // unsigned registration, which would hide a misconfigured gateway.
         if let Some(auth) = &gateway.auth {
@@ -3017,6 +3023,36 @@ mod tests {
         assert!(server.list_gateways(&mut dbtx.to_ref_nc()).await.is_empty());
     }
 
+    /// A rate above one million cannot be represented by the deployed `LNv1`
+    /// fee formula, and used to panic clients that priced it. Refuse to
+    /// store one.
+    #[test_log::test(tokio::test)]
+    async fn registration_with_absurd_proportional_fee_is_rejected() {
+        let (server, db, _tg) = build_server();
+        let mut dbtx = db.begin_transaction().await;
+        let mut dbtx = dbtx.to_ref_with_prefix_module_id(42).0;
+
+        let gateway_id = random_pub_key();
+        let mut absurd = announcement(gateway_id, "https://gw.example/v1");
+        absurd.info.fees.proportional_millionths = 1_000_001;
+
+        let err = server
+            .register_gateway(&mut dbtx.to_ref_nc(), absurd)
+            .await
+            .expect_err("a fee larger than the payment must be rejected");
+        assert!(err.to_string().contains("exceeds the payment itself"));
+        assert!(server.list_gateways(&mut dbtx.to_ref_nc()).await.is_empty());
+
+        let mut at_limit = announcement(gateway_id, "https://gw.example/v1");
+        at_limit.info.fees.proportional_millionths = 1_000_000;
+
+        server
+            .register_gateway(&mut dbtx.to_ref_nc(), at_limit)
+            .await
+            .expect("a fee equal to the payment is within the bound");
+        assert_eq!(server.list_gateways(&mut dbtx.to_ref_nc()).await.len(), 1);
+    }
+
     /// A captured proof must not be replayable to roll a gateway back to
     /// settings it has since moved off.
     #[test_log::test(tokio::test)]
```
