# [?] fix: prevent panic on etherscan client creation failure in test command (#13395)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-02-11
Source: https://github.com/foundry-rs/foundry/commit/9abaa538b6831ed4e2e8d25392647661aecf735a
Type: security-commit

## Details
fix: prevent panic on etherscan client creation failure in test command (#13395)

## Patch
### crates/evm/traces/src/identifier/external.rs
```diff
@@ -61,7 +61,14 @@ impl ExternalIdentifier {
         }
         if let Some(config) = config {
             debug!(target: "evm::traces::external", chain=?config.chain, url=?config.api_url, "using etherscan identifier");
-            fetchers.push(Arc::new(EtherscanFetcher::new(config.into_client()?)));
+            match config.into_client() {
+                Ok(client) => {
+                    fetchers.push(Arc::new(EtherscanFetcher::new(client)));
+                }
+                Err(err) => {
+                    warn!(target: "evm::traces::external", ?err, "failed to create etherscan client");
+                }
+            }
         }
         if fetchers.is_empty() {
             debug!(target: "evm::traces::external", "no fetchers enabled");
```
