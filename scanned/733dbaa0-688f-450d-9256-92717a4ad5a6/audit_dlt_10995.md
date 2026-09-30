# [?] avoiding side effects in out of bounds log operations

## Summary
Severity: Unknown
Chain: ZK
Component: iden3/circom
Published: 2023-01-16
Source: https://github.com/iden3/circom/commit/90b8fb5a22c11cfd47df98d2a690547dfa3bb586
Type: security-commit

## Details
avoiding side effects in out of bounds log operations

## Patch
### code_producers/src/wasm_elements/wasm_code_generator.rs
```diff
@@ -1127,13 +1127,12 @@ pub fn copy_fr_in_shared_rw_memory_generator(producer: &WASMProducer) -> Vec<Was
     let header = "(func $copyFr2SharedRWMemory (type $_t_i32)".to_string(); //receives address to be copied
     instructions.push(header);
     instructions.push(" (param $p i32)".to_string());
+    let pos = producer.get_shared_rw_memory_start() - 8;
+    instructions.push(set_constant(&pos.to_string()));
     instructions.push(get_local("$p"));
+    instructions.push(call("$Fr_copy"));
+    instructions.push(set_constant(&pos.to_string()));
     instructions.push(call("$Fr_toLongNormal"));
-    instructions.push(get_local("$p"));
-    instructions.push(set_constant("8"));
-    instructions.push(add32());
-    instructions.push(set_constant(&producer.get_shared_rw_memory_start().to_string()));
-    instructions.push(call("$Fr_int_copy"));
     instructions.push(")".to_string());
     instructions
 }
@@ -1155,13 +1154,12 @@ pub fn get_witness_generator(producer: &WASMProducer) -> Vec<WasmInstruction> {
     instructions.push(set_constant(&producer.get_signal_memory_start().to_string()));
     instructions.push(add32()); // address of the signal in the signal Memory
     instructions.push(set_local("$c"));
+    let pos = producer.get_shared_rw_memory_start() - 8;
+    instructions.push(set_constant(&pos.to_string()));
     instructions.push(get_local("$c"));
+    instructions.push(call("$Fr_copy"));
+    instructions.push(set_constant(&pos.to_string()));
     instructions.push(call("$Fr_toLongNormal"));
-    instructions.push(get_local("$c"));
-    instructions.push(set_constant("8"));
-    instructions.push(add32());
-    instructions.push(set_constant(&producer.get_shared_rw_memory_start().to_string()));
-    instructions.push(call("$Fr_int_copy"));
     instructions.push(")".to_string());
     instructions
 }
```
