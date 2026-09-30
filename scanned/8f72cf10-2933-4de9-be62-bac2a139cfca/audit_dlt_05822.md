# [?] chore(ci): ignore RUSTSEC-2025-0161 in cargo audit (#15565)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-04-15
Source: https://github.com/near/nearcore/commit/d4891df1530ba81ea96eb1ba4865832b100f61d2
Type: security-commit

## Details
chore(ci): ignore RUSTSEC-2025-0161 in cargo audit (#15565)

Ignore RUSTSEC-2025-0161 (libsecp256k1 unmaintained) in cargo audit.
Every version of aurora-engine-transactions pulls it in — via
aurora-engine-precompiles in 1.1, or aurora-engine-sdk in 1.2+. In the
main workspace it's only a dev-dependency (test-loop-tests,
integration-tests). It is also a transitive dependency of the wallet
contract (separate workspace in
runtime/near-wallet-contract/implementation/).

## Patch
### .cargo/audit.toml
```diff
@@ -61,6 +61,12 @@ ignore = [
     # TODO(#15435): Update object_store once the maintainers release a version with reqwest 0.13+
     "RUSTSEC-2026-0049",
 
+    # libsecp256k1 is unmaintained, but every version of aurora-engine-transactions pulls it in
+    # (via aurora-engine-precompiles in 1.1, or aurora-engine-sdk in 1.2+). In the main workspace
+    # it's only a dev-dependency (test-loop-tests, integration-tests). It is also a transitive
+    # dependency of the wallet contract (separate workspace in runtime/near-wallet-contract/implementation/).
+    "RUSTSEC-2025-0161",
+
     # RUSTSEC-2026-0097: rand unsoundness only triggers when rand's `log` feature is on and a
     # custom `log::Log` logger calls `rand::rng()` on reseed. Neither applies here: the `log`
     # feature is not enabled (check with `cargo tree -e features --workspace | grep 'rand feature'`)
```
