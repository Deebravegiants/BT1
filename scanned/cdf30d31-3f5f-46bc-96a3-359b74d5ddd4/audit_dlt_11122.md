# [?] Fix deadlock

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2020-12-03
Source: https://github.com/matter-labs/zksync/commit/6e90d55969a7c1fa969171379e7e7e20e3221d51
Type: security-commit

## Details
Fix deadlock

## Patch
### core/bin/zksync_api/src/api_server/rest/v1/accounts/mod.rs
```diff
@@ -35,7 +35,6 @@ fn unable_to_find_token(token_id: TokenId) -> anyhow::Error {
 // Additional parser because actix-web doesn't understand enums in path extractor.
 fn parse_account_query(query: String) -> Result<AccountQuery, ApiError> {
     query.parse().map_err(|err| {
-        dbg!(&err);
         ApiError::bad_request("Must be specified either an account ID or an account address.")
             .detail(format!("An error occurred: {}", err))
     })
@@ -100,6 +99,10 @@ impl ApiAccountsData {
             .account_state(query)
             .await?;
 
+        // Drop storage access to avoid deadlocks.
+        // TODO Rewrite `TokensDBCache` logic to make such errors impossible. ZKS-169
+        drop(storage);
+
         // TODO This code uses same logic as the old RPC, but I'm not sure that if it is correct.
         let (account_id, account) = if let Some(state) = account_state.committed {
             state
```
