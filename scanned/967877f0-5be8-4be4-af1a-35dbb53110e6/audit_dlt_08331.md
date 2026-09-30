# [?] [bytecode verifier] fix edge overflow in borrow graph (#17771)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-10-06
Source: https://github.com/aptos-labs/aptos-core/commit/56ea7f6b86ce674dd7a96141180489d469f909d7
Type: security-commit

## Details
[bytecode verifier] fix edge overflow in borrow graph (#17771)

## Patch
### third_party/move/move-bytecode-verifier/src/reference_safety/abstract_state.rs
```diff
@@ -379,12 +379,15 @@ impl AbstractState {
         mut_: bool,
         local: LocalIndex,
     ) -> PartialVMResult<AbstractValue> {
-        // nothing to check in case borrow is mutable since the frame cannot have an full borrow/
-        // epsilon outgoing edge
         if !mut_ && self.is_local_mutably_borrowed(local) {
             return Err(self.error(StatusCode::BORROWLOC_EXISTS_BORROW_ERROR, offset));
         }
 
+        // The frame can end up being fully borrowed because of borrow edge overflow.
+        if mut_ && self.has_full_borrows(self.frame_root()) {
+            return Err(self.error(StatusCode::BORROWLOC_EXISTS_BORROW_ERROR, offset));
+        }
+
         let new_id = self.new_ref(mut_);
         self.add_local_borrow(local, new_id);
         Ok(AbstractValue::Reference(new_id))
```

### third_party/move/move-bytecode-verifier/transactional-tests/tests/reference_safety/borrow_edge_overflow.exp
```diff
@@ -0,0 +1,19 @@
+processed 2 tasks
+task 0 lines 1-146:  publish [module 0x66::a]
+Error: Unable to publish module '0000000000000000000000000000000000000000000000000000000000000066::a'. Got VMError: {
+    major_status: BORROWLOC_EXISTS_BORROW_ERROR,
+    sub_status: None,
+    location: 0x66::a,
+    indices: [(FunctionDefinition, 1)],
+    offsets: [(FunctionDefinitionIndex(1), 73)],
+}
+task 1 lines 149-149:  run 0x66::a::foo --signers 0x66 --verbose
+Error: Function execution failed with VMError: {
+    message: Linker Error: Module 0000000000000000000000000000000000000000000000000000000000000066::a doesn't exist,
+    major_status: LINKER_ERROR,
+    sub_status: None,
+    location: undefined,
+    indices: [],
+    offsets: [],
+    exec_state: None,
+}
```

### third_party/move/move-bytecode-verifier/transactional-tests/tests/reference_safety/borrow_edge_overflow.masm
```diff
@@ -0,0 +1,149 @@
+//# publish
+module 0x66::a
+
+use 0x1::signer
+
+
+struct S has copy+drop
+	  x: u8
+
+
+entry public fun bar(a: &mut S, b: &mut S)
+	ld_u8 123
+	pack S
+	move_loc a
+	write_ref
+
+	move_loc b
+	read_ref
+	unpack S
+
+	ld_u8 123
+	eq
+	br_false ok
+
+	ld_u64 42
+	abort 
+
+	ok:
+
+	ret
+
+entry public fun foo(s: &signer)
+	local a: &mut S
+	local b: &mut S
+	local vv: S
+	local v0: S
+	local v1: S
+	local v2: S
+	local v3: S
+	local v4: S
+	local v5: S
+	local v6: S
+	local v7: S
+	local v8: S
+	local v9: S
+	local v_aliased: S
+
+	ld_u8 0
+	pack S
+	st_loc vv
+
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+	copy_loc vv
+
+	st_loc v_aliased
+	st_loc v0
+	st_loc v1
+	st_loc v2
+	st_loc v3
+	st_loc v4
+	st_loc v5
+	st_loc v6
+	st_loc v7
+	st_loc v8
+	st_loc v9
+
+	mut_borrow_loc v0
+	st_loc a
+	ld_false
+	br_true r
+
+	mut_borrow_loc v1
+	st_loc a
+	ld_false
+	br_true r
+
+	mut_borrow_loc v2
+	st_loc a
+	ld_false
+	br_true r
+
+
+	mut_borrow_loc v3
+	st_loc a
+	ld_false
+	br_true r
+
+
+	mut_borrow_loc v4
+	st_loc a
+	ld_false
+	br_true r
+
+
+	mut_borrow_loc v5
+	st_loc a
+	ld_false
+	br_true r
+
+	mut_borrow_loc v6
+	st_loc a
+	ld_false
+	br_true r
+
+	mut_borrow_loc v7
+	st_loc a
+	ld_false
+	br_true r
+
+	mut_borrow_loc v8
+	st_loc a
+	ld_false
+	br_true r
+
+	mut_borrow_loc v9
+	st_loc a
+	ld_false
+	br_true r
+
+	mut_borrow_loc vv
+	st_loc a
+	ld_false
+	br_true r
+
+	mut_borrow_loc v_aliased
+	st_loc a
+	ld_false
+	br_true r
+
+
+r:
+
+	mut_borrow_loc v_aliased
+	move_loc a
+	call bar
+
+	ret
+
+
+//# run 0x66::a::foo --signers 0x66 --verbose
\ No newline at end of file
```
