# [?] chore: skip RUSTSEC-2026-0173 (#6638)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2026-06-09
Source: https://github.com/chainflip-io/chainflip-backend/commit/f400afab066298320c405524f9cfa02d31df4b42
Type: security-commit

## Details
chore: skip RUSTSEC-2026-0173 (#6638)

## Patch
### .cargo/config.toml
```diff
@@ -81,6 +81,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2026-0114: wasmtime panic during memory allocation. Dependency of substrate.
 # - RUSTSEC-2026-0118: DoS vector in hickory-proto which is used by libp2p. Dependency of substrate, related to DNS resolution. Low risk.
 # - RUSTSEC-2026-0119: DoS vector in hickory-proto which is used by libp2p. Dependency of substrate, related to DNS resolution. Low risk.
+# - RUSTSEC-2026-0173: proc-macro-error2 unmaintained. Build-time proc-macro helper, transitive dependency of `subxt-macro`. Not a runtime security concern.
 
 #
 cf-audit = '''
@@ -129,6 +130,7 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2026-0114
 	--ignore RUSTSEC-2026-0118
 	--ignore RUSTSEC-2026-0119
+	--ignore RUSTSEC-2026-0173
 '''
 
 [build]
```
