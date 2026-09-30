# [?] Fix bug in NoteManager revealed by these new panics!

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-05-14
Source: https://github.com/penumbra-zone/penumbra/commit/80cecab4bc81033abd5ae98db847542b9405aa12
Type: security-commit

## Details
Fix bug in NoteManager revealed by these new panics!

## Patch
### crates/shielded-pool/src/component/note_manager.rs
```diff
@@ -99,10 +99,10 @@ pub trait NoteManager: StateWrite {
 
         // 2. Finally, record it to be inserted into the compact block:
         let mut payloads: im::Vector<(tct::Position, Commitment)> = self
-            .object_get(state_key::pending_notes())
+            .object_get(state_key::pending_rolled_up_notes())
             .unwrap_or_default();
         payloads.push_back((position, note_commitment));
-        self.object_put(state_key::pending_notes(), payloads);
+        self.object_put(state_key::pending_rolled_up_notes(), payloads);
     }
 
     async fn pending_note_payloads(&self) -> im::Vector<(tct::Position, NotePayload, NoteSource)> {
@@ -111,7 +111,7 @@ pub trait NoteManager: StateWrite {
     }
 
     async fn pending_rolled_up_payloads(&self) -> im::Vector<(tct::Position, Commitment)> {
-        self.object_get(state_key::pending_notes())
+        self.object_get(state_key::pending_rolled_up_notes())
             .unwrap_or_default()
     }
 
```
