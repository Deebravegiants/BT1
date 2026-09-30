# [?] chore: ignore RUSTSEC-2026-0009 for cargo audit. (#6405)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2026-02-06
Source: https://github.com/chainflip-io/chainflip-backend/commit/a491107cdbc7ebac786267ab792fbd5adf6aa6a5
Type: security-commit

## Details
chore: ignore RUSTSEC-2026-0009 for cargo audit. (#6405)

* chore: ignore RUSTSEC-2026-0009 for cargo audit.

* chore: change asset amount in FoK test.

## Patch
### .cargo/config.toml
```diff
@@ -60,6 +60,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2025-0134: Unmaintained rustls-pemfile crate (version 1.0.4 and 2.2.0). Substrate dependency.
 # - RUSTSEC-2025-0141: Unmaintained bincode crate. Wasmtime dependency.
 # - RUSTSEC-2026-0002: Unsoundness in the lru crate. Our immediate dependency is patched, but not the transitive dependency, which is limited to libp2p-identify and smoldot crates.
+# - RUSTSEC-2026-0009: Medium severity, but only exploitable if user-provided strings are parsed into a time format by the `time` dependency.
 cf-audit = '''
 audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2021-0139
@@ -88,6 +89,7 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2025-0141
 	--ignore RUSTSEC-2026-0002
 	--ignore RUSTSEC-2026-0007
+	--ignore RUSTSEC-2026-0009
 '''
 
 [build]
```

### bouncer/tests/fill_or_kill.ts
```diff
@@ -199,7 +199,7 @@ export async function testFillOrKill(testContext: TestContext) {
     (subcf) => testMinPriceRefund(subcf, Assets.Sol, 10, true),
     (subcf) => testMinPriceRefund(subcf, Assets.Sol, 1000, true),
     (subcf) => testMinPriceRefund(subcf, Assets.ArbUsdc, 5, false, true),
-    (subcf) => testMinPriceRefund(subcf, Assets.Usdc, 1, false, true),
+    (subcf) => testMinPriceRefund(subcf, Assets.Usdc, 20, false, true),
     (subcf) => testMinPriceRefund(subcf, Assets.SolUsdc, 1, false, true),
     (subcf) => testMinPriceRefund(subcf, Assets.ArbEth, 5, true, true),
     (subcf) => testMinPriceRefund(subcf, Assets.Sol, 10, true, true),
```
