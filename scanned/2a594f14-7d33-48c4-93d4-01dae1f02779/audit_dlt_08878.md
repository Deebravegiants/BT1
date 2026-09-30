# [?] Fix LS deadlock (#3288)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2023-06-01
Source: https://github.com/starkware-libs/cairo/commit/210b7ec576ee53138d7f00ea4a03472263950ae4
Type: security-commit

## Details
Fix LS deadlock (#3288)

## Patch
### crates/cairo-lang-language-server/src/lib.rs
```diff
@@ -122,6 +122,7 @@ impl NotificationService {
 pub struct Backend {
     pub client: Client,
     // TODO(spapini): Remove this once we support ParallelDatabase.
+    // State mutex should only be taken after db mutex is taken, to avoid deadlocks.
     pub db_mutex: tokio::sync::Mutex<RootDatabase>,
     pub state_mutex: tokio::sync::Mutex<State>,
     pub scarb: ScarbService,
@@ -179,11 +180,11 @@ impl Backend {
 
     // Refresh diagnostics and send diffs to client.
     async fn refresh_diagnostics(&self) {
+        let db = self.db().await;
         let mut state = self.state_mutex.lock().await;
 
         // Get all files. Try to go over open files first.
         let mut files_set: OrderedHashSet<_> = state.open_files.iter().copied().collect();
-        let db = self.db().await;
         for crate_id in db.crates() {
             for module_id in db.crate_modules(crate_id).iter() {
                 for file_id in db.module_files(*module_id).unwrap_or_default() {
```
