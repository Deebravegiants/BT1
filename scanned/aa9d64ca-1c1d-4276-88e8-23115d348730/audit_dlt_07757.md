# [?] fix: rm unsound transmute (#15373)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-03-28
Source: https://github.com/paradigmxyz/reth/commit/2c6380c7e0a328edc05ea468a0b71331c7cc497d
Type: security-commit

## Details
fix: rm unsound transmute (#15373)

## Patch
### crates/cli/commands/src/db/tui.rs
```diff
@@ -30,12 +30,6 @@ static CMDS: [(&str, &str); 6] = [
     ("G", "Go to a specific page"),
 ];
 
-/// Modified version of the [`ListState`] struct that exposes the `offset` field.
-/// Used to make the [`DbListTUI`] keys clickable.
-struct ExpListState {
-    pub(crate) offset: usize,
-}
-
 #[derive(Default, Eq, PartialEq)]
 pub(crate) enum ViewMode {
     /// Normal list view mode
@@ -321,14 +315,7 @@ where
             MouseEventKind::ScrollUp => app.previous(),
             // TODO: This click event can be triggered outside of the list widget.
             MouseEventKind::Down(_) => {
-                // SAFETY: The pointer to the app's state will always be valid for
-                // reads here, and the source is larger than the destination.
-                //
-                // This is technically unsafe, but because the alignment requirements
-                // in both the source and destination are the same and we can ensure
-                // that the pointer to `app.state` is valid for reads, this is safe.
-                let state: ExpListState = unsafe { std::mem::transmute_copy(&app.list_state) };
-                let new_idx = (e.row as usize + state.offset).saturating_sub(1);
+                let new_idx = (e.row as usize + app.list_state.offset()).saturating_sub(1);
                 if new_idx < app.entries.len() {
                     app.list_state.select(Some(new_idx));
                 }
```
