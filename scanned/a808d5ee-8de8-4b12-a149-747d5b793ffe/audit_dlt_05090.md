# [?] fix: dont panic on note msgs on contracts with no notes (#24852)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-07-21
Source: https://github.com/AztecProtocol/aztec-packages/commit/0b4cfbc78c07c42e59e3af4530f769e51e1ff438
Type: security-commit

## Details
fix: dont panic on note msgs on contracts with no notes (#24852)

A contract with no notes might otherwise panic if e.g. it processed an
offchain message related to one. I also made PXE skip the standard
contracts that have no notes and events, both to avoid such a situation
and because there's no need to do it.

(cherry picked from commit dfcdea6756263c09e179861071fa4c64572ebb2d)

## Patch
### noir-projects/aztec-nr/aztec/src/macros/aztec/compute_note_hash_and_nullifier.nr
```diff
@@ -44,10 +44,12 @@ pub(crate) comptime fn generate_contract_library_methods_compute_note_hash_and_n
 
 comptime fn generate_contract_library_method_compute_note_hash() -> Quoted {
     if NOTES.len() == 0 {
-        // Contracts with no notes still implement this function to avoid having special-casing, the implementation
-        // simply throws immediately.
+        // Contracts with no notes still implement this function to avoid having special-casing. Since the contract
+        // declares no note types there is never a note to hash, so we return `Option::none()`. This will cause any
+        // messages related to (non-existing) notes to be simply skipped, mirroring the unknown-note-type branch of the
+        // with-notes implementation.
         quote {
-            /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+            /// This contract does not use private notes, so this function always returns `Option::none()`.
             ///
             /// This function is automatically injected by the `#[aztec]` macro.
             #[contract_library_method]
@@ -59,7 +61,7 @@ comptime fn generate_contract_library_method_compute_note_hash() -> Quoted {
                 _contract_address: aztec::protocol::address::AztecAddress,
                 _randomness: Field,
             ) -> Option<Field> {
-                panic(f"This contract does not use private notes")
+                Option::none()
             }
         }
     } else {
@@ -155,10 +157,12 @@ comptime fn generate_contract_library_method_compute_note_hash() -> Quoted {
 
 comptime fn generate_contract_library_method_compute_note_nullifier() -> Quoted {
     if NOTES.len() == 0 {
-        // Contracts with no notes still implement this function to avoid having special-casing, the implementation
-        // simply throws immediately.
+        // Contracts with no notes still implement this function to avoid having special-casing. Since the contract
+        // declares no note types there is never a note to nullify, so we return `Option::none()`. This will cause any
+        // messages related to (non-existing) notes to be simply skipped, mirroring the unknown-note-type branch of the
+        // with-notes implementation.
         quote {
-            /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+            /// This contract does not use private notes, so this function always returns `Option::none()`.
             ///
             /// This function is automatically injected by the `#[aztec]` macro.
             #[contract_library_method]
@@ -171,7 +175,7 @@ comptime fn generate_contract_library_method_compute_note_nullifier() -> Quoted
                 _contract_address: aztec::protocol::address::AztecAddress,
                 _randomness: Field,
             ) -> Option<Field> {
-                panic(f"This contract does not use private notes")
+                Option::none()
             }
         }
     } else {
```

### noir-projects/contract-snapshots/tests/snapshots/expand/avm_gadgets_test_contract/snapshots__expanded.snap
```diff
@@ -2,7 +2,6 @@
 source: tests/snapshots.rs
 expression: stdout
 ---
-
 use aztec::macros::aztec;
 use aztec::macros::aztec;
 
@@ -119,20 +118,20 @@ contract AvmGadgetsTest {
         })
     }
 
-    /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+    /// This contract does not use private notes, so this function always returns `Option::none()`.
     /// 
     /// This function is automatically injected by the `#[aztec]` macro.
     #[contract_library_method]
     unconstrained fn _compute_note_hash(_packed_note: BoundedVec<Field, 8>, _owner: aztec::protocol::address::AztecAddress, _storage_slot: Field, _note_type_id: Field, _contract_address: aztec::protocol::address::AztecAddress, _randomness: Field) -> Option<Field> {
-        panic(f"This contract does not use private notes")
+        Option::<Field>::none()
     }
 
-    /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+    /// This contract does not use private notes, so this function always returns `Option::none()`.
     /// 
     /// This function is automatically injected by the `#[aztec]` macro.
     #[contract_library_method]
     unconstrained fn _compute_note_nullifier(_unique_note_hash: Field, _packed_note: BoundedVec<Field, 8>, _owner: aztec::protocol::address::AztecAddress, _storage_slot: Field, _note_type_id: Field, _contract_address: aztec::protocol::address::AztecAddress, _randomness: Field) -> Option<Field> {
-        panic(f"This contract does not use private notes")
+        Option::<Field>::none()
     }
 
     /// Receives offchain messages into this contract's offchain inbox for subsequent processing.
```

### noir-projects/contract-snapshots/tests/snapshots/expand/avm_test_contract/snapshots__expanded.snap
```diff
@@ -2,7 +2,6 @@
 source: tests/snapshots.rs
 expression: stdout
 ---
-
 use aztec::macros::aztec;
 use aztec::macros::aztec;
 
@@ -709,20 +708,20 @@ pub contract AvmTest {
         })
     }
 
-    /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+    /// This contract does not use private notes, so this function always returns `Option::none()`.
     /// 
     /// This function is automatically injected by the `#[aztec]` macro.
     #[contract_library_method]
     unconstrained fn _compute_note_hash(_packed_note: BoundedVec<Field, 8>, _owner: AztecAddress, _storage_slot: Field, _note_type_id: Field, _contract_address: AztecAddress, _randomness: Field) -> Option<Field> {
-        panic(f"This contract does not use private notes")
+        Option::<Field>::none()
     }
 
-    /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+    /// This contract does not use private notes, so this function always returns `Option::none()`.
     /// 
     /// This function is automatically injected by the `#[aztec]` macro.
     #[contract_library_method]
     unconstrained fn _compute_note_nullifier(_unique_note_hash: Field, _packed_note: BoundedVec<Field, 8>, _owner: AztecAddress, _storage_slot: Field, _note_type_id: Field, _contract_address: AztecAddress, _randomness: Field) -> Option<Field> {
-        panic(f"This contract does not use private notes")
+        Option::<Field>::none()
     }
 
     /// Receives offchain messages into this contract's offchain inbox for subsequent processing.
```

### noir-projects/contract-snapshots/tests/snapshots/expand/public_fns_with_emit_repro_contract/snapshots__expanded.snap
```diff
@@ -2,7 +2,6 @@
 source: tests/snapshots.rs
 expression: stdout
 ---
-
 use aztec::macros::aztec;
 use aztec::macros::aztec;
 
@@ -140,20 +139,20 @@ pub contract PublicFnsWithEmitRepro {
         })
     }
 
-    /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+    /// This contract does not use private notes, so this function always returns `Option::none()`.
     /// 
     /// This function is automatically injected by the `#[aztec]` macro.
     #[contract_library_method]
     unconstrained fn _compute_note_hash(_packed_note: BoundedVec<Field, 8>, _owner: aztec::protocol::address::AztecAddress, _storage_slot: Field, _note_type_id: Field, _contract_address: aztec::protocol::address::AztecAddress, _randomness: Field) -> Option<Field> {
-        panic(f"This contract does not use private notes")
+        Option::<Field>::none()
     }
 
-    /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+    /// This contract does not use private notes, so this function always returns `Option::none()`.
     /// 
     /// This function is automatically injected by the `#[aztec]` macro.
     #[contract_library_method]
     unconstrained fn _compute_note_nullifier(_unique_note_hash: Field, _packed_note: BoundedVec<Field, 8>, _owner: aztec::protocol::address::AztecAddress, _storage_slot: Field, _note_type_id: Field, _contract_address: aztec::protocol::address::AztecAddress, _randomness: Field) -> Option<Field> {
-        panic(f"This contract does not use private notes")
+        Option::<Field>::none()
     }
 
     /// Receives offchain messages into this contract's offchain inbox for subsequent processing.
```

### noir-projects/contract-snapshots/tests/snapshots/expand/storage_proof_test_contract/snapshots__expanded.snap
```diff
@@ -2,7 +2,6 @@
 source: tests/snapshots.rs
 expression: stdout
 ---
-
 use aztec::macros::aztec;
 use aztec::macros::aztec;
 
@@ -86,20 +85,20 @@ contract StorageProofTest {
         })
     }
 
-    /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+    /// This contract does not use private notes, so this function always returns `Option::none()`.
     /// 
     /// This function is automatically injected by the `#[aztec]` macro.
     #[contract_library_method]
     unconstrained fn _compute_note_hash(_packed_note: BoundedVec<Field, 8>, _owner: AztecAddress, _storage_slot: Field, _note_type_id: Field, _contract_address: AztecAddress, _randomness: Field) -> Option<Field> {
-        panic(f"This contract does not use private notes")
+        Option::<Field>::none()
     }
 
-    /// This contract does not use private notes, so this function should never be called as it will unconditionally fail.
+    /// This contract does not use private notes, so this function always returns `Option::none()`.
     /// 
     /// This function is automatically injected by the `#[aztec]` macro.
     #[contract_library_method]
     unconstrained fn _compute_note_nullifier(_unique_note_hash: Field, _packed_note: BoundedVec<Field, 8>, _owner: AztecAddress, _storage_slot: Field, _note_type_id: Field, _contract_address: AztecAddress, _randomness: Field) -> Option<Field> {
-        panic(f"This contract does not use private notes")
+        Option::<Field>::none()
     }
 
     /// Receives offchain messages into this contract's offchain inbox for subsequent processing.
```

### noir-projects/noir-contracts/Nargo.toml
```diff
@@ -60,6 +60,7 @@ members = [
     "contracts/test/nested_utility_contract",
     "contracts/test/no_constructor_contract",
     "contracts/test/note_hash_and_nullifier/note_hash_and_nullifier_contract",
+    "contracts/test/no_notes_contract",
     "contracts/test/note_getter_contract",
     "contracts/test/offchain_effect_contract",
     "contracts/test/offchain_payment_contract",
```

### noir-projects/noir-contracts/contracts/test/no_notes_contract/Nargo.toml
```diff
@@ -0,0 +1,8 @@
+[package]
+name = "no_notes_contract"
+authors = [""]
+compiler_version = ">=0.25.0"
+type = "contract"
+
+[dependencies]
+aztec = { path = "../../../../aztec-nr/aztec" }
```

### noir-projects/noir-contracts/contracts/test/no_notes_contract/src/main.nr
```diff
@@ -0,0 +1,74 @@
+mod test;
+
+use aztec::macros::aztec;
+
+/// A minimal contract that declares no note types, used to test the macro-generated no-notes
+/// `_compute_note_hash`, `_compute_note_nullifier` and (deprecated) `_compute_note_hash_and_nullifier` functions.
+#[aztec]
+pub contract NoNotes {
+    use aztec::{
+        messages::{discovery::NoteHashAndNullifier as NoteHashAndNullifierResult, logs::note::MAX_NOTE_PACKED_LEN},
+        protocol::address::AztecAddress,
+    };
+
+    #[contract_library_method]
+    pub unconstrained fn test_compute_note_hash(
+        packed_note: BoundedVec<Field, MAX_NOTE_PACKED_LEN>,
+        owner: AztecAddress,
+        storage_slot: Field,
+        note_type_id: Field,
+        contract_address: AztecAddress,
+        randomness: Field,
+    ) -> Option<Field> {
+        _compute_note_hash(
+            packed_note,
+            owner,
+            storage_slot,
+            note_type_id,
+            contract_address,
+            randomness,
+        )
+    }
+
+    #[contract_library_method]
+    pub unconstrained fn test_compute_note_nullifier(
+        unique_note_hash: Field,
+        packed_note: BoundedVec<Field, MAX_NOTE_PACKED_LEN>,
+        owner: AztecAddress,
+        storage_slot: Field,
+        note_type_id: Field,
+        contract_address: AztecAddress,
+        randomness: Field,
+    ) -> Option<Field> {
+        _compute_note_nullifier(
+            unique_note_hash,
+            packed_note,
+            owner,
+            storage_slot,
+            note_type_id,
+            contract_address,
+            randomness,
+        )
+    }
+
+    #[contract_library_method]
+    pub unconstrained fn test_compute_note_hash_and_nullifier(
+        packed_note: BoundedVec<Field, MAX_NOTE_PACKED_LEN>,
+        owner: AztecAddress,
+        storage_slot: Field,
+        note_type_id: Field,
+        contract_address: AztecAddress,
+        randomness: Field,
+        note_nonce: Field,
+    ) -> Option<NoteHashAndNullifierResult> {
+        _compute_note_hash_and_nullifier(
+            packed_note,
+            owner,
+            storage_slot,
+            note_type_id,
+            contract_address,
+            randomness,
+            note_nonce,
+        )
+    }
+}
```

### noir-projects/noir-contracts/contracts/test/no_notes_contract/src/test.nr
```diff
@@ -0,0 +1,50 @@
+use crate::NoNotes;
+use aztec::protocol::address::AztecAddress;
+
+// The contract declares no note types, so there is never a note to hash or nullify: every input must be skipped
+// (return `Option::none()`) regardless of its contents, so that malicious messages about non-existent notes are
+// ignored.
+
+#[test]
+unconstrained fn compute_note_hash_skips() {
+    let result = NoNotes::test_compute_note_hash(
+        BoundedVec::from_array([42]),
+        AztecAddress::zero(),
+        0,
+        0xdeadbeef,
+        AztecAddress::zero(),
+        0,
+    );
+
+    assert(result.is_none());
+}
+
+#[test]
+unconstrained fn compute_note_nullifier_skips() {
+    let result = NoNotes::test_compute_note_nullifier(
+        0,
+        BoundedVec::from_array([42]),
+        AztecAddress::zero(),
+        0,
+        0xdeadbeef,
+        AztecAddress::zero(),
+        0,
+    );
+
+    assert(result.is_none());
+}
+
+#[test]
+unconstrained fn compute_note_hash_and_nullifier_skips() {
+    let result = NoNotes::test_compute_note_hash_and_nullifier(
+        BoundedVec::from_array([42]),
+        AztecAddress::zero(),
+        0,
+        0xdeadbeef,
+        AztecAddress::zero(),
+        0,
+        0,
+    );
+
+    assert(result.is_none());
+}
```

### yarn-project/pxe/src/contract/helpers.ts
```diff
@@ -1,10 +1,10 @@
-import { isProtocolContract } from '@aztec/protocol-contracts';
 import type { FunctionCall, FunctionSelector } from '@aztec/stdlib/abi';
 import type { AztecAddress } from '@aztec/stdlib/aztec-address';
 import type { BlockHeader } from '@aztec/stdlib/tx';
 
 import type { ContractStore } from '../storage/contract_store/contract_store.js';
 import type { ContractClassService } from './contract_class_service.js';
+import { isSkipSyncContract } from './skip_sync_contracts.js';
 
 export async function syncScope(
   contractAddress: AztecAddress,
@@ -15,8 +15,8 @@ export async function syncScope(
   utilityExecutor: (privateSyncCall: FunctionCall, scopes: AztecAddress[]) => Promise<any>,
   scope: AztecAddress,
 ) {
-  // Protocol contracts don't have private state to sync
-  if (isProtocolContract(contractAddress)) {
+  // Some canonical contracts hold no private state, so there is nothing to sync (see `skipSyncContracts`).
+  if (isSkipSyncContract(contractAddress)) {
     return;
   }
 
```

### yarn-project/pxe/src/contract/skip_sync_contracts.test.ts
```diff
@@ -0,0 +1,63 @@
+import { ProtocolContractAddress } from '@aztec/protocol-contracts';
+import { STANDARD_AUTH_REGISTRY_ADDRESS } from '@aztec/standard-contracts/auth-registry/constants';
+import { STANDARD_HANDSHAKE_REGISTRY_ADDRESS } from '@aztec/standard-contracts/handshake-registry/constants';
+import { STANDARD_MULTI_CALL_ENTRYPOINT_ADDRESS } from '@aztec/standard-contracts/multi-call-entrypoint/constants';
+import { STANDARD_PUBLIC_CHECKS_ADDRESS } from '@aztec/standard-contracts/public-checks/constants';
+import type { FunctionCall } from '@aztec/stdlib/abi';
+import { AztecAddress } from '@aztec/stdlib/aztec-address';
+import type { BlockHeader } from '@aztec/stdlib/tx';
+
+import { jest } from '@jest/globals';
+import { type MockProxy, mock } from 'jest-mock-extended';
+
+import type { ContractStore } from '../storage/contract_store/contract_store.js';
+import type { ContractClassService } from './contract_class_service.js';
+import { syncScope } from './helpers.js';
+import { isSkipSyncContract } from './skip_sync_contracts.js';
+
+describe('isSkipSyncContract', () => {
+  it('skips the protocol contracts, the auth registry, the multicall entrypoint and the public checks', () => {
+    const skipped = [
+      ...Object.values(ProtocolContractAddress),
+      STANDARD_AUTH_REGISTRY_ADDRESS,
+      STANDARD_MULTI_CALL_ENTRYPOINT_ADDRESS,
+      STANDARD_PUBLIC_CHECKS_ADDRESS,
+    ];
+    for (const address of skipped) {
+      expect(isSkipSyncContract(address)).toBe(true);
+    }
+  });
+
+  it('does not skip contracts that hold private state', async () => {
+    // The handshake registry declares a note, so its private state must still be synced.
+    expect(isSkipSyncContract(STANDARD_HANDSHAKE_REGISTRY_ADDRESS)).toBe(false);
+    expect(isSkipSyncContract(await AztecAddress.random())).toBe(false);
+  });
+});
+
+describe('syncScope', () => {
+  let contractStore: MockProxy<ContractStore>;
+  let contractClassService: MockProxy<ContractClassService>;
+  let utilityExecutor: jest.Mock<(call: FunctionCall, scopes: AztecAddress[]) => Promise<any>>;
+
+  beforeEach(() => {
+    contractStore = mock<ContractStore>();
+    contractClassService = mock<ContractClassService>();
+    utilityExecutor = jest.fn<(call: FunctionCall, scopes: AztecAddress[]) => Promise<any>>();
+  });
+
+  it('does not run sync_state for a skipped contract', async () => {
+    await syncScope(
+      STANDARD_MULTI_CALL_ENTRYPOINT_ADDRESS,
+      contractStore,
+      contractClassService,
+      mock<BlockHeader>(),
+      null,
+      utilityExecutor,
+      await AztecAddress.random(),
+    );
+
+    expect(contractClassService.getCurrentClassId).not.toHaveBeenCalled();
+    expect(utilityExecutor).not.toHaveBeenCalled();
+  });
+});
```

### yarn-project/pxe/src/contract/skip_sync_contracts.ts
```diff
@@ -0,0 +1,23 @@
+import { ProtocolContractAddress } from '@aztec/protocol-contracts';
+import { STANDARD_AUTH_REGISTRY_ADDRESS } from '@aztec/standard-contracts/auth-registry/constants';
+import { STANDARD_MULTI_CALL_ENTRYPOINT_ADDRESS } from '@aztec/standard-contracts/multi-call-entrypoint/constants';
+import { STANDARD_PUBLIC_CHECKS_ADDRESS } from '@aztec/standard-contracts/public-checks/constants';
+import type { AztecAddress } from '@aztec/stdlib/aztec-address';
+
+/**
+ * Canonical contracts that hold no private state and are therefore never synced.
+ *
+ * The protocol contracts (registries, fee juice) plus the standard AuthRegistry, MultiCallEntrypoint and PublicChecks
+ * declare no notes and no events, so their macro-generated `sync_state` has nothing to discover.
+ */
+export const skipSyncContracts: AztecAddress[] = [
+  ...Object.values(ProtocolContractAddress),
+  STANDARD_AUTH_REGISTRY_ADDRESS,
+  STANDARD_MULTI_CALL_ENTRYPOINT_ADDRESS,
+  STANDARD_PUBLIC_CHECKS_ADDRESS,
+];
+
+/** Returns whether the given contract should be skipped during private state synchronization. */
+export function isSkipSyncContract(address: AztecAddress): boolean {
+  return skipSyncContracts.some(a => a.equals(address));
+}
```
