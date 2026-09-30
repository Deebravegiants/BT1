# [?] fix(RUSTSEC-2024-0370)!: bump `clap` to latest, removing transitive

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2024-09-12
Source: https://github.com/bitcoindevkit/bdk/commit/d802d00a06035bec582eb5aadf0281f26bff6acd
Type: security-commit

## Details
fix(RUSTSEC-2024-0370)!: bump `clap` to latest, removing transitive
dependency on `proc-macro-error`.

In #1593 it's mentioned that `proc-macro-error` is unmaintained for the
past few years, with no fix other than using proc-macro-error2 instead.

As on our scenario it's merely a transitive dependency of `clap`,
through `clap_derive` feature, which in latest releases doesn't depend on
`proc-macro-error` we can just bump it to latest.

It's valid to note that by bumping it, both examples that relies on clap
are no longer MSRV (1.63) compliant.

## Patch
### example-crates/example_cli/Cargo.toml
```diff
@@ -12,7 +12,7 @@ bdk_file_store = { path = "../../crates/file_store" }
 bitcoin = { version = "0.32.0", features = ["base64"], default-features = false }
 
 anyhow = "1"
-clap = { version = "3.2.23", features = ["derive", "env"] }
+clap = { version = "4.5.17", features = ["derive", "env"] }
 rand = "0.8"
 serde = { version = "1", features = ["derive"] }
 serde_json = "1.0"
```

### example-crates/example_wallet_rpc/Cargo.toml
```diff
@@ -10,5 +10,5 @@ bdk_wallet = { path = "../../crates/wallet", features = ["file_store"] }
 bdk_bitcoind_rpc = { path = "../../crates/bitcoind_rpc" }
 
 anyhow = "1"
-clap = { version = "3.2.25", features = ["derive", "env"] }
+clap = { version = "4.5.17", features = ["derive", "env"] }
 ctrlc = "2.0.1"
```
