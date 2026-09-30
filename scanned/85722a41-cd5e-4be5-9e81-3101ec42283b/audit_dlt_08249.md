# [?] Fix rust toolchain race condition (#10036)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-06-02
Source: https://github.com/firedancer-io/firedancer/commit/d06cf96550aef52a0403eb34891c007f3d70a1e1
Type: security-commit

## Details
Fix rust toolchain race condition (#10036)

Co-authored-by: Richard Patel <ripatel@jumptrading.com>

## Patch
### deps.sh
```diff
@@ -378,7 +378,8 @@ check () {
     case "$choice" in
       y|Y)
         echo "[+] Installing rustup"
-        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
+        # Keep this in sync with agave/rust-toolchain.toml
+        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.95.0 --profile minimal
         source "$HOME/.cargo/env"
         ;;
       *)
```
