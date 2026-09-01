# [?] fix: address CI failures - unused panic import and admin_auth test flakiness

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-02-02
Source: https://github.com/fedimint/fedimint/commit/bc6c0b4553769f6fed3c6918469a4c4deb5222dd
Type: security-commit

## Details
fix: address CI failures - unused panic import and admin_auth test flakiness

- Conditionally import panic module only for non-WASM targets in jit.rs
- Add retry logic to admin_auth test to handle transient iroh connection issues

Signed-off-by: Devansh Vashisht <devansh.vashisht.ug24@nsut.ac.in>
