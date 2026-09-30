# [?] pd: avoid crash by ignoring missing root errors loading the nct from an empty state

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-03-30
Source: https://github.com/penumbra-zone/penumbra/commit/ad30f163057d6f4ef9876cbcea0704b970a4a14e
Type: security-commit

## Details
pd: avoid crash by ignoring missing root errors loading the nct from an empty state

## Patch
### pd/src/components/shielded_pool.rs
```diff
@@ -246,11 +246,11 @@ impl ShieldedPool {
     /// This is an associated function rather than a method,
     /// so that we can call it in the constructor to get the NCT.
     async fn get_nct(overlay: &Overlay) -> Result<NoteCommitmentTree> {
-        if let Some(bytes) = overlay
+        if let Ok(Some(bytes)) = overlay
             .lock()
             .await
             .get(b"shielded_pool/nct_data".into())
-            .await?
+            .await
         {
             bincode::deserialize(&bytes).map_err(Into::into)
         } else {
```
