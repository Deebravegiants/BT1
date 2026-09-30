# [?] Merge pull request #6 from opentensor/security/ghsa-2026-002-swap-hotkey-v2-proxy-gap

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/c52dac0ff96f5aee41a51a0b16d44f741d8ca12c
Type: security-commit

## Details
Merge pull request #6 from opentensor/security/ghsa-2026-002-swap-hotkey-v2-proxy-gap

NonFungible proxy denylist omits live `swap_hotkey_v2` (call 72), letting a scoped delegate reassign a victim's hotkey identity

## Patch
### runtime/src/lib.rs
```diff
@@ -683,6 +683,7 @@ subtensor_macros::define_proxy_filters! {
         SubtensorModule::clear_coldkey_swap_announcement,
         SubtensorModule::dispute_coldkey_swap,
         SubtensorModule::swap_hotkey,
+        SubtensorModule::swap_hotkey_v2,
     }
 
     Transfer => allow {
@@ -754,6 +755,7 @@ subtensor_macros::define_proxy_filters! {
 
     SwapHotkey => allow {
         SubtensorModule::swap_hotkey,
+        SubtensorModule::swap_hotkey_v2,
     }
 
     SubnetLeaseBeneficiary => allow {
```

### runtime/tests/ghsa_repro.rs
```diff
@@ -122,3 +122,28 @@ fn ghsa_2026_001_noncritical_is_not_a_fund_protection_type() {
         "NonCritical already allows transfer_stake, so coldkey-swap adds no new capability"
     );
 }
+
+/// GHSA-2026-002 — NonFungible denies the deprecated swap_hotkey (call 70) but ALLOWS the
+/// live swap_hotkey_v2 (call 72); and the SwapHotkey allow-list permits only call 70.
+#[test]
+fn ghsa_2026_002_nonfungible_allows_swap_hotkey_v2_gap() {
+    // The denylist blocks the old call but not the live superset.
+    assert!(
+        !ProxyType::NonFungible.filter(&swap_hotkey_v1()),
+        "precondition: NonFungible denies deprecated swap_hotkey (call 70)"
+    );
+    assert!(
+        !ProxyType::NonFungible.filter(&swap_hotkey_v2()),
+        "regression (GHSA-2026-002 fixed): NonFungible must DENY the live swap_hotkey_v2 (call 72)"
+    );
+
+    // Inverse breakage: SwapHotkey allow-list only permits the deprecated call.
+    assert!(
+        ProxyType::SwapHotkey.filter(&swap_hotkey_v1()),
+        "precondition: SwapHotkey allows deprecated swap_hotkey (call 70)"
+    );
+    assert!(
+        ProxyType::SwapHotkey.filter(&swap_hotkey_v2()),
+        "regression (GHSA-2026-002 fixed): SwapHotkey must ALLOW the live swap_hotkey_v2 (call 72)"
+    );
+}
```
