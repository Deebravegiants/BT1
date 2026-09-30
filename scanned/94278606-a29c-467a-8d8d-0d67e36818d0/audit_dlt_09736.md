# [?] fix(lnv2): make PaymentFee Add overflow explicit

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-03
Source: https://github.com/fedimint/fedimint/commit/e8fce2d37293b205e4528047cf2c040a084b12b3
Type: security-commit

## Details
fix(lnv2): make PaymentFee Add overflow explicit

## Patch
### modules/fedimint-lnv2-common/src/gateway_api.rs
```diff
@@ -247,10 +247,14 @@ impl PaymentFee {
 
 impl Add for PaymentFee {
     type Output = PaymentFee;
+
     fn add(self, rhs: Self) -> Self::Output {
         PaymentFee {
-            base: self.base + rhs.base,
-            parts_per_million: self.parts_per_million + rhs.parts_per_million,
+            base: self.base.checked_add(rhs.base).expect("fee base overflow"),
+            parts_per_million: self
+                .parts_per_million
+                .checked_add(rhs.parts_per_million)
+                .expect("fee parts per million overflow"),
         }
     }
 }
@@ -354,4 +358,28 @@ mod tests {
         };
         assert!(ok.is_within(&PaymentFee::SEND_FEE_LIMIT));
     }
+
+    #[test]
+    #[should_panic(expected = "fee base overflow")]
+    fn payment_fee_add_panics_on_base_overflow() {
+        let _ = PaymentFee {
+            base: Amount::from_msats(u64::MAX),
+            parts_per_million: 0,
+        } + PaymentFee {
+            base: Amount::from_msats(1),
+            parts_per_million: 0,
+        };
+    }
+
+    #[test]
+    #[should_panic(expected = "fee parts per million overflow")]
+    fn payment_fee_add_panics_on_ppm_overflow() {
+        let _ = PaymentFee {
+            base: Amount::ZERO,
+            parts_per_million: u64::MAX,
+        } + PaymentFee {
+            base: Amount::ZERO,
+            parts_per_million: 1,
+        };
+    }
 }
```
