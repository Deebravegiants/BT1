# [?] [bug fix] Remove incorrect overflow guard (#1034)

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2023-04-12
Source: https://github.com/move-language/move/commit/dfef14a838c8dd6399e933b77426a03f40e69c4c
Type: security-commit

## Details
[bug fix] Remove incorrect overflow guard (#1034)

- Removed incorrect overflow guard
- Added tests

## Patch
### language/move-binary-format/src/file_format.rs
```diff
@@ -1757,11 +1757,6 @@ impl Bytecode {
             "Program counter out of bounds"
         );
 
-        // Return early to prevent overflow if pc is hiting the end of max number of instructions allowed (u16::MAX).
-        if pc > u16::max_value() - 2 {
-            return vec![];
-        }
-
         let bytecode = &code[pc as usize];
         let mut v = vec![];
 
```

### language/move-binary-format/src/unit_tests/binary_tests.rs
```diff
@@ -20,10 +20,10 @@ fn test_max_number_of_bytecode() {
     for _ in 0..u16::MAX - 1 {
         nops.push(Bytecode::Nop);
     }
-    nops.push(Bytecode::Ret);
+    nops.push(Bytecode::Branch(0));
 
     let result = Bytecode::get_successors(u16::MAX - 1, &nops);
-    assert!(result.is_empty());
+    assert_eq!(result, vec![0]);
 }
 
 proptest! {
```

### language/move-bytecode-verifier/src/regression_tests/reference_analysis.rs
```diff
@@ -3,11 +3,15 @@
 
 use move_binary_format::{
     file_format::{
-        empty_module, AbilitySet, AddressIdentifierIndex, Bytecode::*, CodeUnit, Constant,
-        FieldDefinition, FunctionDefinition, FunctionHandle, FunctionHandleIndex, IdentifierIndex,
-        ModuleHandle, ModuleHandleIndex, Signature, SignatureIndex, SignatureToken::*,
+        empty_module, AbilitySet, AddressIdentifierIndex,
+        Bytecode::{self, *},
+        CodeUnit, Constant, FieldDefinition, FunctionDefinition, FunctionHandle,
+        FunctionHandleIndex, IdentifierIndex, ModuleHandle, ModuleHandleIndex, Signature,
+        SignatureIndex,
+        SignatureToken::{self, *},
         StructDefinition, StructDefinitionIndex, StructFieldInformation, StructHandle,
-        StructHandleIndex, TypeSignature, Visibility, Visibility::*,
+        StructHandleIndex, TypeSignature, Visibility,
+        Visibility::*,
     },
     CompiledModule,
 };
@@ -16,6 +20,8 @@ use move_core_types::{
 };
 use std::str::FromStr;
 
+use crate::VerifierConfig;
+
 #[test]
 fn unbalanced_stack_crash() {
     let mut module = empty_module();
@@ -208,3 +214,110 @@ fn borrow_graph() {
     let res = crate::verify_module(&module);
     assert!(res.is_ok());
 }
+
+#[test]
+fn indirect_code() {
+    use Bytecode::*;
+    let v = 0;
+    let v_ref = 1;
+    let x = 2;
+    let x_ref = 3;
+    let vsig = SignatureIndex(2);
+    let next = 16;
+    let mut code = vec![
+        // x = 10; x_ref = &mut x;
+        LdU64(10),
+        StLoc(x),
+        MutBorrowLoc(x),
+        StLoc(x_ref),
+        // v = vector[100, 1000]; v_ref = &mut v
+        LdU64(100),
+        LdU64(1000),
+        VecPack(vsig, 2),
+        StLoc(v),
+        MutBorrowLoc(v),
+        StLoc(v_ref),
+        // if (*x_ref == 0) return;
+        CopyLoc(x_ref),
+        ReadRef,
+        LdU64(0),
+        Eq,
+        BrFalse(next),
+        Ret,
+    ];
+    assert_eq!(code.len(), next as usize);
+    code.extend(vec![
+        // creates dangling reference on second iteration
+        // _ = vec_pop_back(x_ref)
+        CopyLoc(v_ref),
+        VecPopBack(vsig),
+        Pop,
+        // *x_ref = 0
+        LdU64(0),
+        CopyLoc(x_ref),
+        WriteRef,
+        // x_ref = vec_mut_borrow(v_ref, 0);
+        CopyLoc(v_ref),
+        LdU64(0),
+        VecMutBorrow(vsig),
+        StLoc(x_ref),
+    ]);
+    let nops = vec![Nop; (u16::MAX as usize) - code.len() - 1];
+    code.extend(nops);
+    code.push(Branch(10));
+    assert_eq!(code.len(), (u16::MAX as usize));
+    let module = CompiledModule {
+        version: 5,
+        self_module_handle_idx: ModuleHandleIndex(0),
+        module_handles: vec![ModuleHandle {
+            address: AddressIdentifierIndex(0),
+            name: IdentifierIndex(0),
+        }],
+        struct_handles: vec![],
+        function_handles: vec![FunctionHandle {
+            module: ModuleHandleIndex(0),
+            name: IdentifierIndex(0),
+            parameters: SignatureIndex(0),
+            return_: SignatureIndex(0),
+            type_parameters: vec![],
+        }],
+        field_handles: vec![],
+        friend_decls: vec![],
+        struct_def_instantiations: vec![],
+        function_instantiations: vec![],
+        field_instantiations: vec![],
+        signatures: vec![
+            Signature(vec![]),
+            Signature(vec![
+                SignatureToken::Vector(Box::new(SignatureToken::U64)),
+                SignatureToken::MutableReference(Box::new(SignatureToken::Vector(Box::new(
+                    SignatureToken::U64,
+                )))),
+                SignatureToken::U64,
+                SignatureToken::MutableReference(Box::new(SignatureToken::U64)),
+            ]),
+            Signature(vec![SignatureToken::U64]),
+        ],
+        identifiers: vec![Identifier::new("a").unwrap()],
+        address_identifiers: vec![AccountAddress::ONE],
+        constant_pool: vec![],
+        metadata: vec![],
+        struct_defs: vec![],
+        function_defs: vec![FunctionDefinition {
+            function: FunctionHandleIndex(0),
+            visibility: Visibility::Public,
+            is_entry: false,
+            acquires_global_resources: vec![],
+            code: Some(CodeUnit {
+                locals: SignatureIndex(1),
+                code,
+            }),
+        }],
+    };
+
+    let res = crate::verify_module_with_config(&VerifierConfig::unbounded(), &module).unwrap_err();
+    assert_eq!(
+        res.major_status(),
+        StatusCode::VEC_UPDATE_EXISTS_MUTABLE_BORROW_ERROR
+    );
+}
```

### language/move-bytecode-verifier/transactional-tests/tests/control_flow/last_jump_unconditional_drop.exp
```diff
@@ -0,0 +1,10 @@
+processed 2 tasks
+
+task 1 'run'. lines 17-5495:
+Error: Script execution failed with VMError: {
+    major_status: STLOC_UNSAFE_TO_DESTROY_ERROR,
+    sub_status: None,
+    location: script,
+    indices: [],
+    offsets: [(FunctionDefinitionIndex(0), 65530)],
+}
```

### language/move-bytecode-verifier/transactional-tests/tests/control_flow/last_jump_unconditional_reference.exp
```diff
@@ -0,0 +1,10 @@
+processed 1 task
+
+task 0 'run'. lines 1-5478:
+Error: Script execution failed with VMError: {
+    major_status: VEC_UPDATE_EXISTS_MUTABLE_BORROW_ERROR,
+    sub_status: None,
+    location: script,
+    indices: [],
+    offsets: [(FunctionDefinitionIndex(0), 65529)],
+}
```
