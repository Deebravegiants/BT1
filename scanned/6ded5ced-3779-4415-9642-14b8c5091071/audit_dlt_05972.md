# [?] Merge pull request #7 from opentensor/security/ghsa-2026-003-owner-proxy-set-sn-owner-hotkey-alias-bypass

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/5902428c50d4fe5ffe5f4df9a9e2f6ddb139cca1
Type: security-commit

## Details
Merge pull request #7 from opentensor/security/ghsa-2026-003-owner-proxy-set-sn-owner-hotkey-alias-bypass

Owner proxy `except sudo_set_sn_owner_hotkey` carve-out is bypassable via the duplicate alias `sudo_set_subnet_owner_hotkey`

## Patch
### runtime/src/lib.rs
```diff
@@ -705,6 +705,7 @@ subtensor_macros::define_proxy_filters! {
         SubtensorModule::update_symbol,
     } except {
         AdminUtils::sudo_set_sn_owner_hotkey,
+        AdminUtils::sudo_set_subnet_owner_hotkey,
     }
 
     NonCritical => deny {
```

### runtime/tests/ghsa_repro.rs
```diff
@@ -147,3 +147,19 @@ fn ghsa_2026_002_nonfungible_allows_swap_hotkey_v2_gap() {
         "regression (GHSA-2026-002 fixed): SwapHotkey must ALLOW the live swap_hotkey_v2 (call 72)"
     );
 }
+
+/// GHSA-2026-003 — the Owner proxy excepts sudo_set_sn_owner_hotkey (call 67) but the
+/// duplicate alias sudo_set_subnet_owner_hotkey (call 64) is allowed by the AdminUtils::*
+/// wildcard, bypassing the carve-out.
+#[test]
+fn ghsa_2026_003_owner_proxy_set_owner_hotkey_alias_bypass() {
+    assert!(
+        !ProxyType::Owner.filter(&set_sn_owner_hotkey_c67()),
+        "precondition: Owner correctly excepts sudo_set_sn_owner_hotkey (call 67)"
+    );
+    assert!(
+        !ProxyType::Owner.filter(&set_subnet_owner_hotkey_c64()),
+        "regression (GHSA-2026-003 fixed): Owner must DENY the alias sudo_set_subnet_owner_hotkey (call 64), \
+         which calls the same do_set_sn_owner_hotkey backend"
+    );
+}
```
