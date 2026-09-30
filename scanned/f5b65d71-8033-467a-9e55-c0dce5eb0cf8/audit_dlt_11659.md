# [?] Merge rust-bitcoin/rust-bitcoin#4838: Fix overflow during *_ceil FeeRate conversions

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-08-13
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/3b8f25935ed532e1c36535c30123c56c6e95eb49
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#4838: Fix overflow during *_ceil FeeRate conversions

dc2de6adf5e5d38b71b7319f4c1e78854a472297 Fix overflow during *_ceil FeeRate conversions (Shing Him Ng)

Pull request description:

  During some work on updating the fuzz targets, I came across an overflow error during this call when `FeeRate::MAX` was passed in:
  
  ```rust
  script.minimal_non_dust_custom(fee_rate);
  ```
  
  This calls `FeeRate::to_sat_per_kvb_ceil()` under the covers, which was where the overflow was happening. I also updated similar functions that would have run into the same issue


ACKs for top commit:
  tcharding:
    ACK dc2de6adf5e5d38b71b7319f4c1e78854a472297
  apoelstra:
    ACK dc2de6adf5e5d38b71b7319f4c1e78854a472297; successfully ran local tests


Tree-SHA512: 15a325a6ca5c87bbab8c6b8a16804c67ffeda27e260393631e99ae657c7a6b075b015a225a83912a729ecf102d170510498a00d6fe4bf566e4b474bc6cb351b5

## Patch
### units/src/fee_rate/mod.rs
```diff
@@ -106,19 +106,19 @@ impl FeeRate {
     pub const fn to_sat_per_kwu_floor(self) -> u64 { self.to_sat_per_mvb() / 4_000 }
 
     /// Converts to sat/kwu rounding up.
-    pub const fn to_sat_per_kwu_ceil(self) -> u64 { (self.to_sat_per_mvb() + 3_999) / 4_000 }
+    pub const fn to_sat_per_kwu_ceil(self) -> u64 { self.to_sat_per_mvb().saturating_add(3_999) / 4_000 }
 
     /// Converts to sat/vB rounding down.
     pub const fn to_sat_per_vb_floor(self) -> u64 { self.to_sat_per_mvb() / 1_000_000 }
 
     /// Converts to sat/vB rounding up.
-    pub const fn to_sat_per_vb_ceil(self) -> u64 { (self.to_sat_per_mvb() + 999_999) / 1_000_000 }
+    pub const fn to_sat_per_vb_ceil(self) -> u64 { self.to_sat_per_mvb().saturating_add(999_999) / 1_000_000 }
 
     /// Converts to sat/kvb rounding down.
     pub const fn to_sat_per_kvb_floor(self) -> u64 { self.to_sat_per_mvb() / 1_000 }
 
     /// Converts to sat/kvb rounding up.
-    pub const fn to_sat_per_kvb_ceil(self) -> u64 { (self.to_sat_per_mvb() + 999) / 1_000 }
+    pub const fn to_sat_per_kvb_ceil(self) -> u64 { self.to_sat_per_mvb().saturating_add(999) / 1_000 }
 
     /// Checked multiplication.
     ///
@@ -400,6 +400,11 @@ mod tests {
         // sat/kvb: 2_000_400 / 1_000 = 2_000.4
         assert_eq!(fee_rate.to_sat_per_kvb_floor(), 2_000);
         assert_eq!(fee_rate.to_sat_per_kvb_ceil(), 2_001);
+
+        let max = FeeRate::MAX;
+        assert_eq!(max.to_sat_per_kwu_ceil(), u64::MAX / 4_000);
+        assert_eq!(max.to_sat_per_vb_ceil(), u64::MAX / 1_000_000);
+        assert_eq!(max.to_sat_per_kvb_ceil(), u64::MAX / 1_000);
     }
 
     #[test]
```
