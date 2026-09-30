# [?] [token-cli] Fix panicking behavior from `sign_only` (#7527)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2024-11-27
Source: https://github.com/solana-labs/solana-program-library/commit/dcfc02b7409d74d9cfc18d71f0348b060cb40b21
Type: security-commit

## Details
[token-cli] Fix panicking behavior from `sign_only` (#7527)

fix panicking behavior from `sign_only`

## Patch
### token/cli/src/config.rs
```diff
@@ -106,7 +106,7 @@ impl<'a> Config<'a> {
             CommitmentConfig::confirmed(),
             DEFAULT_CONFIRM_TX_TIMEOUT,
         ));
-        let sign_only = matches.is_present(SIGN_ONLY_ARG.name);
+        let sign_only = matches.try_contains_id(SIGN_ONLY_ARG.name).unwrap_or(false);
         let program_client: Arc<dyn ProgramClient<ProgramRpcClientSendTransaction>> = if sign_only {
             let blockhash = matches
                 .get_one::<Hash>(BLOCKHASH_ARG.name)
```
