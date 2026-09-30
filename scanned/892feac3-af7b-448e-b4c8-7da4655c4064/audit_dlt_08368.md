# [?] [move-prover] replacing plus func to avoid overflow

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-02-22
Source: https://github.com/move-language/move/commit/21f4baf69d5866d8cb2253dbade66f8daa91c31b
Type: security-commit

## Details
[move-prover] replacing plus func to avoid overflow

Closes: #7682

## Patch
### language/move-prover/bytecode/src/memory_instrumentation_v2.rs
```diff
@@ -179,7 +179,7 @@ impl<'a> Instrumenter<'a> {
 
     fn new_attr_id(&mut self, loc: Loc) -> AttrId {
         let attr_id = AttrId::new(self.next_attr_id);
-        self.next_attr_id += 1;
+        self.next_attr_id = usize::saturating_add(self.next_attr_id, 1);
         self.new_locations.insert(attr_id, loc);
         attr_id
     }
```
