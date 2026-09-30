# [?] fix(cheatcodes): expectSafeMemory panics on short/unexpanded CALL calldata to the cheatcode address (#16576)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-08
Source: https://github.com/foundry-rs/foundry/commit/a1f8b77e70259c3fdbac6a3bca637b482d928da0
Type: security-commit

## Details
fix(cheatcodes): expectSafeMemory panics on short/unexpanded CALL calldata to the cheatcode address (#16576)

* fix(cheatcodes): expectSafeMemory panics on short/unexpanded CALL calldata to the cheatcode address

The stopExpectSafeMemory() special case in the CALL-opcode branch of
check_mem_opcodes read args_size bytes of calldata via
interpreter.memory.slice_len(args_offset, args_size), then indexed the
first SELECTOR_LEN (4) bytes to compare against the selector - without
checking that the slice was actually at least 4 bytes long, or that
[args_offset, args_offset + args_size) was within the interpreter's
current (pre-expansion) memory buffer.

This hook runs in step(), before the CALL opcode itself has expanded
memory to cover its own args - so a disallowed CALL to the cheatcode
address with short or out-of-range calldata is a live condition, not
theoretical. Two ways to trigger it:
  - args_size < 4: memory_word[..SELECTOR_LEN] panics with
    'range end index 4 out of range for slice of length 0' (repro'd
    live via forge test, panic at inspector.rs:3924).
  - args_offset + args_size past current memory.size(): slice_len ->
    slice_range hits revm's debug_unreachable! (panics in debug
    builds, UB in release builds per revm's own documented Safety
    section).

Guard both cases before calling slice_len, falling through to the
existing disallowed_mem_write() path instead - which is what should
happen for a genuinely out-of-range CALL to the cheatcode address
anyway.

Added two regression tests to MemSafety.t.sol covering both cases.

closes nothing - filed independently, no corresponding issue was open.

* chore: add changelog and trim comments

* chore: trim safe memory comments

Shorten the added explanations while preserving the relevant invariants. Correct release metadata and recovery coverage where needed.

---------

Co-authored-by: stevencartavia <112043913+stevencartavia@users.noreply.github.com>
Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>

## Patch
### .changelog/safe-memory-call-calldata.md
```diff
@@ -0,0 +1,6 @@
+---
+forge: patch
+foundry-cheatcodes: patch
+---
+
+Prevented `expectSafeMemory` from panicking on calls to the cheatcode address with short or unexpanded calldata.
```

### crates/cheatcodes/src/inspector.rs
```diff
@@ -3947,9 +3947,14 @@ impl<FEN: FoundryEvmNetwork> Cheatcodes<FEN> {
                             if to == CHEATCODE_ADDRESS {
                                 let args_offset = try_or_return!(interpreter.stack.peek(3)).saturating_to::<usize>();
                                 let args_size = try_or_return!(interpreter.stack.peek(4)).saturating_to::<usize>();
-                                let memory_word = interpreter.memory.slice_len(args_offset, args_size);
-                                if memory_word[..SELECTOR_LEN] == stopExpectSafeMemoryCall::SELECTOR {
-                                    return
+                                // CALL has not expanded input memory yet.
+                                if args_size >= SELECTOR_LEN
+                                    && args_offset.saturating_add(args_size) <= interpreter.memory.size()
+                                {
+                                    let memory_word = interpreter.memory.slice_len(args_offset, args_size);
+                                    if memory_word[..SELECTOR_LEN] == stopExpectSafeMemoryCall::SELECTOR {
+                                        return
+                                    }
                                 }
                             }
 
```

### testdata/default/cheats/MemSafety.t.sol
```diff
@@ -159,6 +159,36 @@ contract MemSafetyTest is Test {
         _doCallReturnData(address(sc), payload, 0x80, 0x60);
     }
 
+    ////////////////////////////////////////////////////////////////
+    //        CALL with short/out-of-range calldata to `vm`        //
+    ////////////////////////////////////////////////////////////////
+
+    /// @dev Short calldata must revert without panicking.
+    /// forge-config: default.allow_internal_expect_revert = true
+    function testExpectSafeMemory_CALL_shortCalldataToCheatcodeAddress() public {
+        vm.expectSafeMemory(0x80, 0xA0);
+
+        vm.expectRevert();
+
+        // Empty calldata and a return buffer outside the allowed range.
+        assembly {
+            pop(call(gas(), 0x7109709ECfa91a80626fF3989D68f67F5b1DD12D, 0x00, 0x00, 0x00, 0x200, 0x20))
+        }
+    }
+
+    /// @dev Unexpanded calldata must revert without reading past memory.
+    /// forge-config: default.allow_internal_expect_revert = true
+    function testExpectSafeMemory_CALL_unexpandedCalldataToCheatcodeAddress() public {
+        vm.expectSafeMemory(0x80, 0xA0);
+
+        vm.expectRevert();
+
+        // Both calldata and the return buffer lie outside their allowed ranges.
+        assembly {
+            pop(call(gas(), 0x7109709ECfa91a80626fF3989D68f67F5b1DD12D, 0x00, 0x100000, 0x04, 0x200, 0x20))
+        }
+    }
+
     ////////////////////////////////////////////////////////////////
     //                          CALLCODE                          //
     ////////////////////////////////////////////////////////////////
```
