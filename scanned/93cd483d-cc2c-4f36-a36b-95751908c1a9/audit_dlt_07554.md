# [?] pd: fix crash from TCT misuse

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-05-18
Source: https://github.com/penumbra-zone/penumbra/commit/ca97d194df29d75c9bf6e86e737d1e46eaa7ec9d
Type: security-commit

## Details
pd: fix crash from TCT misuse

This fixes a bug that slipped in during the review process for #807: changing
the code to not `.expect` on errors from the TCT left behind a duplicate API
call with an `expect`, which then panicked, causing a chain halt on the very
first epoch transition.

## Patch
### shielded-pool/src/component.rs
```diff
@@ -373,9 +373,6 @@ impl ShieldedPool {
         // 1. Insert it into the NCT
         self.note_commitment_tree
             .append(&note_payload.note_commitment);
-        self.tiered_commitment_tree
-            .insert(penumbra_tct::Witness::Forget, note_payload.note_commitment)
-            .expect("inserting a commitment into the TCT should never fail");
 
         // TODO: replace this with an `expect!` when this is consensus-critical
         if let Err(e) = self
```
