# [M] Inconsistency in Fee Calculation in `update_fees` Function

## Summary
Severity: Medium
Chain: Smart contract
Component: Kintsu
Published: 2024-05-16
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/18
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x155e6094f1322438cb40a4f20ef832d05b21b7329de6541a5c2e28d288d6586e
**Severity:** medium

**Description:**
**Description:** In the current implementation of the `update_fees` function, the calculation of fee accumulation does not consider the owner's virtual shares (`total_shares_virtual`). Instead, it only considers `total_shares_minted`.  owners shares should be considered in total shares just like `get_total_shares` function. This leads to the owner losing some fee.

**Impact:** The owner is losing some funds due to the inconsistency in fee calculation.

**Revised Code File (Optional):**
```diff
@@ -417,7 +417,7 @@ impl VaultData {
 
         // Calculate fee accumulation since last update
         if time > 0 {
-            let virtual_shares = self.total_shares_minted * self.fee_percentage as u128 / BIPS as u128;
+            let virtual_shares = (self.total_shares_minted + self.total_shares_virtual)* self.fee_percentage as u128 / BIPS as u128;
             let time_weighted_virtual_shares = virtual_shares * time as u128 / YEAR as u128;
 
             self.total_shares_virtual += time_weighted_virtual_shares;
@@ -432,7 +432,7 @@ impl VaultData {
 
         if time > 0 {
             // Calculate fee accumulation since last update
-            let virtual_shares = self.total_shares_minted * self.fee_percentage as u128 / BIPS as u128;
+            let virtual_shares = (self.total_shares_minted + self.total_shares_virtual) * self.fee_percentage as u128 / BIPS as u128;
             let time_weighted_virtual_shares = virtual_shares * time as u128 / YEAR as u128;
             self.total_shares_virtual + time_weighted_virtual_shares
         } else {
```
This revised code snippet ensures that the calculation of fee accumulation in `update_fees` takes into account both `total_shares_minted` and `total_shares_virtual`, providing a more accurate representation of the owner's shares.
