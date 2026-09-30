# [?] Fix nondeterministic constant ordering (#459)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2021-12-15
Source: https://github.com/FuelLabs/sway/commit/585dfc5597b8785f623b1aac85a36b7b49a82f4f
Type: security-commit

## Details
Fix nondeterministic constant ordering (#459)

* Fix nondeterministic constant ordering

* update contract ids

## Patch
### core_lang/src/ident.rs
```diff
@@ -3,6 +3,7 @@ use crate::error::*;
 use crate::parser::Rule;
 use crate::span::Span;
 use pest::iterators::Pair;
+use std::cmp::{Ord, Ordering};
 use std::hash::{Hash, Hasher};
 
 #[derive(Debug, Clone)]
@@ -27,6 +28,17 @@ impl PartialEq for Ident<'_> {
         self.primary_name == other.primary_name
     }
 }
+impl Ord for Ident<'_> {
+    fn cmp(&self, other: &Self) -> Ordering {
+        self.primary_name.cmp(&other.primary_name)
+    }
+}
+
+impl PartialOrd for Ident<'_> {
+    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
+        Some(self.cmp(other))
+    }
+}
 
 impl Eq for Ident<'_> {}
 
```

### core_lang/src/semantic_analysis/namespace.rs
```diff
@@ -11,17 +11,23 @@ use crate::type_engine::*;
 use crate::CallPath;
 use crate::{CompileResult, TypeInfo};
 use crate::{Ident, TypedDeclaration, TypedFunctionDeclaration};
-use std::collections::{HashMap, VecDeque};
+use std::collections::{BTreeMap, HashMap, VecDeque};
 
 type ModuleName = String;
 type TraitName<'a> = CallPath<'a>;
 
 #[derive(Clone, Debug, Default)]
 pub struct Namespace<'sc> {
-    symbols: HashMap<Ident<'sc>, TypedDeclaration<'sc>>,
+    // This is a BTreeMap because we rely on its ordering being consistent. See
+    // [Namespace::get_all_declared_symbols] -- we need that iterator to have a deterministic
+    // order.
+    symbols: BTreeMap<Ident<'sc>, TypedDeclaration<'sc>>,
     implemented_traits: HashMap<(TraitName<'sc>, TypeInfo), Vec<TypedFunctionDeclaration<'sc>>>,
     /// any imported namespaces associated with an ident which is a  library name
-    modules: HashMap<ModuleName, Namespace<'sc>>,
+    // This is a BTreeMap because we rely on its ordering being consistent. See
+    // [Namespace::get_all_imported_modules] -- we need that iterator to have a deterministic
+    // order.
+    modules: BTreeMap<ModuleName, Namespace<'sc>>,
     /// The crate namespace, to be used in absolute importing. This is `None` if the current
     /// namespace _is_ the root namespace.
     use_synonyms: HashMap<Ident<'sc>, Vec<Ident<'sc>>>,
```

### test/src/e2e_vm_tests/test_programs/call_basic_storage/Forc.toml
```diff
@@ -12,7 +12,7 @@ path = "../basic_storage_abi"
 
 [[tx-input]]
 type = "Contract"
-contract-id = "0x145be2230354cac71a59580f00793ec67d2789b983025e1107867560360e007b"
+contract-id = "0x410eab113ce1c194952b92295f3d156bce478633feb2e0117360ff28b034a751"
 utxo-id = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
 balance-root = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
 state-root = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
```

### test/src/e2e_vm_tests/test_programs/call_basic_storage/src/main.sw
```diff
@@ -3,7 +3,7 @@ use basic_storage_abi::StoreU64;
 use basic_storage_abi::StoreU64Request;
 
 fn main() -> u64 {
-  let addr = abi(StoreU64, 0x145be2230354cac71a59580f00793ec67d2789b983025e1107867560360e007b);       
+  let addr = abi(StoreU64, 0x410eab113ce1c194952b92295f3d156bce478633feb2e0117360ff28b034a751);       
   let req = StoreU64Request {
     key: 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff,
     value: 4242
```

### test/src/e2e_vm_tests/test_programs/call_increment_contract/Forc.toml
```diff
@@ -11,7 +11,7 @@ increment_abi = { path = "../increment_abi" }
 
 [[tx-input]]
 type = "Contract"
-contract-id = "0x1c1034f66a300fb0af4d3dcfba823e6237d329ce823f4e2a7f517b330ea5e875"
+contract-id = "0xf7f9d5f37723833e266ff185bd3ded8af980f50703b1719dd47a446af2dabc70"
 utxo-id = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
 balance-root = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
 state-root = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
```

### test/src/e2e_vm_tests/test_programs/call_increment_contract/src/main.sw
```diff
@@ -2,7 +2,7 @@ script;
 use increment_abi::Incrementor;
 use std::constants::ETH_ID;
 fn main() {
-  let abi = abi(Incrementor, 0x1c1034f66a300fb0af4d3dcfba823e6237d329ce823f4e2a7f517b330ea5e875);
+  let abi = abi(Incrementor, 0xf7f9d5f37723833e266ff185bd3ded8af980f50703b1719dd47a446af2dabc70);
   abi.initialize(10000, 0, ETH_ID, 0); // comment this line out to just increment without initializing
   abi.increment(10000, 0, ETH_ID, 5);
   let result = abi.increment(10000, 0, ETH_ID, 5);
```

### test/src/e2e_vm_tests/test_programs/caller_auth_test/Forc.toml
```diff
@@ -11,7 +11,7 @@ auth_testing_abi = { path = "../auth_testing_abi" }
 
 [[tx-input]]
 type = "Contract"
-contract-id = "0x8ca92c2a448e86f374657604a3d62f3d83226f86acfed38e8124cce826926f7f"
+contract-id = "0x27829e78404b18c037b15bfba5110c613a83ea22c718c8b51596e17c9cb1cd6f"
 utxo-id = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
 balance-root = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
 state-root = "0xeeb578f9e1ebfb5b78f8ff74352370c120bc8cacead1f5e4f9c74aafe0ca6bfd"
```

### test/src/e2e_vm_tests/test_programs/caller_auth_test/src/main.sw
```diff
@@ -5,7 +5,7 @@ use std::constants::ETH_ID;
 
 // should be false in the case of a script
 fn main() -> bool {
-  let caller = abi(AuthTesting, 0x8ca92c2a448e86f374657604a3d62f3d83226f86acfed38e8124cce826926f7f);
+  let caller = abi(AuthTesting, 0x27829e78404b18c037b15bfba5110c613a83ea22c718c8b51596e17c9cb1cd6f);
 
   caller.returns_gm_one(1000, 0, ETH_ID, ())
 }
```

### test/src/e2e_vm_tests/test_programs/caller_context_test/Forc.toml
```diff
@@ -11,7 +11,7 @@ context_testing_abi = { path = "../context_testing_abi" }
 
 [[tx-input]]
 type = "Contract"
-contract-id = "0x12522e9f94019df248900cfce4d750977f752ae2034c05fc8d726ecb1a32a9c7"
+contract-id = "0x9f03de8ad53cfcdc5b58e7630c78076a132f434fe74e6b355ac86cd4d0c75e2f"
 utxo-id = "0xad6aaaa1d6fd78f91693ee2cc124fd43d25bd1c015b88b675ee43d6b5e140586"
 balance-root = "0xad6aaaa1d6fd78f91693ee2cc124fd43d25bd1c015b88b675ee43d6b5e140586"
-state-root = "0xad6aaaa1d6fd78f91693ee2cc124fd43d25bd1c015b88b675ee43d6b5e140586"
\ No newline at end of file
+state-root = "0xad6aaaa1d6fd78f91693ee2cc124fd43d25bd1c015b88b675ee43d6b5e140586"
```

### test/src/e2e_vm_tests/test_programs/caller_context_test/src/main.sw
```diff
@@ -7,7 +7,7 @@ fn main() -> bool {
     let gas: u64 = 1000;
     let amount: u64 = 11;
     let test_token_id: b256 = 0x000000000000000000000000000000000000000000000000000000000000002A;
-    let deployed_contract_id = 0x27b323db2cfa318890a8be57b223f40fb364419ba1999cb59eda061aea40730c;
+    let deployed_contract_id = 0x9f03de8ad53cfcdc5b58e7630c78076a132f434fe74e6b355ac86cd4d0c75e2f;
 
     let test_contract = abi(ContextTesting, deployed_contract_id);
 
```
