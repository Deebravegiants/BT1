# [?] Fix txv1 OOB (#12302)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-05-07
Source: https://github.com/anza-xyz/agave/commit/775558cbefadd40175d3fbe070af95748b752bb4
Type: security-commit

## Details
Fix txv1 OOB (#12302)

* Fix txv1 OOB

* remove public constant, fix FILTER_SIZE

* LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET

## Patch
### compute-budget-instruction/src/builtin_programs_filter.rs
```diff
@@ -2,12 +2,11 @@ use {
     solana_builtins_default_costs::{
         BuiltinMigrationFeatureIndex, MAYBE_BUILTIN_KEY, get_builtin_migration_feature_index,
     },
-    solana_packet::PACKET_DATA_SIZE,
     solana_pubkey::Pubkey,
 };
 
 // The maximum number of pubkeys that a packet can contain.
-pub(crate) const FILTER_SIZE: u8 = (PACKET_DATA_SIZE / core::mem::size_of::<Pubkey>()) as u8;
+pub(crate) const FILTER_SIZE: usize = u8::MAX as usize + 1;
 
 #[derive(Clone, Copy, Debug, PartialEq)]
 pub(crate) enum ProgramKind {
@@ -25,13 +24,13 @@ pub(crate) struct BuiltinProgramsFilter {
     // array of slots for all possible static and sanitized program_id_index,
     // each slot indicates if a program_id_index has not been checked (eg, None),
     // or already checked with result (eg, Some(ProgramKind)) that can be reused.
-    program_kind: [Option<ProgramKind>; FILTER_SIZE as usize],
+    program_kind: [Option<ProgramKind>; FILTER_SIZE],
 }
 
 impl BuiltinProgramsFilter {
     pub(crate) fn new() -> Self {
         BuiltinProgramsFilter {
-            program_kind: [None; FILTER_SIZE as usize],
+            program_kind: [None; FILTER_SIZE],
         }
     }
 
@@ -142,8 +141,7 @@ mod test {
     fn test_get_program_kind_out_of_bound_index() {
         let mut test_store = BuiltinProgramsFilter::new();
         assert_eq!(
-            test_store
-                .get_program_kind(FILTER_SIZE as usize + 1, &DUMMY_PROGRAM_ID.parse().unwrap(),),
+            test_store.get_program_kind(FILTER_SIZE + 1, &DUMMY_PROGRAM_ID.parse().unwrap(),),
             ProgramKind::NotBuiltin
         );
     }
```

### compute-budget-instruction/src/compute_budget_program_id_filter.rs
```diff
@@ -8,13 +8,13 @@ pub(crate) struct ComputeBudgetProgramIdFilter {
     // array of slots for all possible static and sanitized program_id_index,
     // each slot indicates if a program_id_index has not been checked (eg, None),
     // or already checked with result (eg, Some(result)) that can be reused.
-    flags: [Option<bool>; FILTER_SIZE as usize],
+    flags: [Option<bool>; FILTER_SIZE],
 }
 
 impl ComputeBudgetProgramIdFilter {
     pub(crate) fn new() -> Self {
         ComputeBudgetProgramIdFilter {
-            flags: [None; FILTER_SIZE as usize],
+            flags: [None; FILTER_SIZE],
         }
     }
 
```

### runtime-transaction/src/signature_details.rs
```diff
@@ -1,8 +1,6 @@
-// static account keys has max
-use {
-    agave_transaction_view::static_account_keys_frame::MAX_STATIC_ACCOUNTS_PER_PACKET as FILTER_SIZE,
-    solana_pubkey::Pubkey, solana_svm_transaction::instruction::SVMInstruction,
-};
+use {solana_pubkey::Pubkey, solana_svm_transaction::instruction::SVMInstruction};
+
+const FILTER_SIZE: usize = u8::MAX as usize + 1;
 
 pub struct PrecompileSignatureDetails {
     pub num_secp256k1_instruction_signatures: u64,
@@ -84,17 +82,17 @@ enum ProgramIdStatus {
 }
 
 struct SignatureDetailsFilter {
-    // array of slots for all possible static and sanitized program_id_index,
+    // array of slots for all possible u8 program_id_index values,
     // each slot indicates if a program_id_index has not been checked, or is
     // already checked with result that can be reused.
-    flags: [Option<ProgramIdStatus>; FILTER_SIZE as usize],
+    flags: [Option<ProgramIdStatus>; FILTER_SIZE],
 }
 
 impl SignatureDetailsFilter {
     #[inline]
     fn new() -> Self {
         Self {
-            flags: [None; FILTER_SIZE as usize],
+            flags: [None; FILTER_SIZE],
         }
     }
 
@@ -208,4 +206,23 @@ mod tests {
         assert_eq!(signature_details.num_ed25519_instruction_signatures, 0);
         assert_eq!(signature_details.num_secp256r1_instruction_signatures, 0);
     }
+
+    #[test]
+    fn test_get_signature_details_program_id_index_above_packet_static_account_limit() {
+        let mut program_ids = vec![Pubkey::new_unique(); FILTER_SIZE];
+        program_ids[38] = solana_sdk_ids::secp256k1_program::ID;
+        program_ids[63] = solana_sdk_ids::ed25519_program::ID;
+        program_ids[u8::MAX as usize] = solana_sdk_ids::secp256r1_program::ID;
+
+        let instructions = [
+            make_instruction(&program_ids, 38, &[2]),
+            make_instruction(&program_ids, 63, &[3]),
+            make_instruction(&program_ids, u8::MAX, &[4]),
+        ];
+
+        let signature_details = get_precompile_signature_details(instructions.into_iter());
+        assert_eq!(signature_details.num_secp256k1_instruction_signatures, 2);
+        assert_eq!(signature_details.num_ed25519_instruction_signatures, 3);
+        assert_eq!(signature_details.num_secp256r1_instruction_signatures, 4);
+    }
 }
```

### runtime/src/bank/tests.rs
```diff
@@ -24,7 +24,6 @@ use {
     },
     agave_feature_set::{self as feature_set, FeatureSet},
     agave_reserved_account_keys::ReservedAccount,
-    agave_transaction_view::static_account_keys_frame::MAX_STATIC_ACCOUNTS_PER_PACKET,
     ahash::AHashMap,
     assert_matches::assert_matches,
     crossbeam_channel::{bounded, unbounded},
@@ -5022,7 +5021,7 @@ fn test_fuzz_instructions() {
         })
         .collect();
     let (bank, _bank_forks) = bank.wrap_with_bank_forks_for_tests();
-    let max_keys = MAX_STATIC_ACCOUNTS_PER_PACKET;
+    let max_keys = 64;
     let keys: Vec<_> = (0..max_keys)
         .enumerate()
         .map(|_| {
@@ -8506,6 +8505,44 @@ fn test_verify_transactions_tx_v1_size_gate_does_not_relax_legacy_or_v0() {
     );
 }
 
+#[test]
+fn test_verify_transactions_tx_v1_precompile_program_id_index_above_packet_limit() {
+    let GenesisConfigInfo { genesis_config, .. } =
+        create_genesis_config_with_leader(42, &solana_pubkey::new_rand(), 42);
+    let mut bank = Bank::new_for_tests(&genesis_config);
+    bank.activate_feature(&feature_set::enable_tx_v1::id());
+
+    let recent_blockhash = Hash::new_unique();
+    let keypair = Keypair::new();
+    let pubkey = keypair.pubkey();
+    let mut account_keys = vec![pubkey];
+    account_keys.extend((1..38).map(|_| Pubkey::new_unique()));
+    account_keys.push(ed25519_program::id());
+    assert_eq!(account_keys.len(), 39);
+
+    let message = v1::Message::new(
+        MessageHeader {
+            num_required_signatures: 1,
+            num_readonly_signed_accounts: 0,
+            num_readonly_unsigned_accounts: 38,
+        },
+        v1::TransactionConfig::empty(),
+        recent_blockhash,
+        account_keys,
+        vec![CompiledInstruction {
+            program_id_index: 38,
+            accounts: vec![],
+            data: vec![],
+        }],
+    );
+    let tx = VersionedTransaction::try_new(VersionedMessage::V1(message), &[&keypair]).unwrap();
+
+    assert!(
+        bank.verify_transaction(tx, TransactionVerificationMode::FullVerification)
+            .is_ok()
+    );
+}
+
 #[test]
 fn test_verify_transactions_instruction_limit() {
     let GenesisConfigInfo { genesis_config, .. } =
```

### transaction-view/src/lib.rs
```diff
@@ -12,7 +12,7 @@ pub mod resolved_transaction_view;
 pub mod result;
 mod sanitize;
 mod signature_frame;
-pub mod static_account_keys_frame;
+mod static_account_keys_frame;
 mod transaction_config_frame;
 pub mod transaction_data;
 mod transaction_frame;
```

### transaction-view/src/static_account_keys_frame.rs
```diff
@@ -7,11 +7,11 @@ use {
     solana_pubkey::Pubkey,
 };
 
-// The packet has a maximum length of 1232 bytes.
+// A legacy/v0 packet has a maximum length of 1232 bytes.
 // This means the maximum number of 32 byte keys is 38.
 // 38 as an min-sized encoded u16 is 1 byte.
 // We can simply read this byte, if it's >38 we can return None.
-pub const MAX_STATIC_ACCOUNTS_PER_PACKET: u8 =
+const LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET: u8 =
     (PACKET_DATA_SIZE / core::mem::size_of::<Pubkey>()) as u8;
 
 /// Contains metadata about the static account keys in a transaction packet.
@@ -27,10 +27,12 @@ impl StaticAccountKeysFrame {
     #[inline(always)]
     pub(crate) fn try_new(bytes: &[u8], offset: &mut usize) -> Result<Self> {
         // Max size must not have the MSB set so that it is size 1.
-        const _: () = assert!(MAX_STATIC_ACCOUNTS_PER_PACKET & 0b1000_0000 == 0);
+        const _: () = assert!(LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET & 0b1000_0000 == 0);
 
         let num_static_accounts = read_byte(bytes, offset)?;
-        if num_static_accounts == 0 || num_static_accounts > MAX_STATIC_ACCOUNTS_PER_PACKET {
+        if num_static_accounts == 0
+            || num_static_accounts > LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET
+        {
             return Err(TransactionViewError::ParseError);
         }
 
@@ -71,7 +73,8 @@ mod tests {
 
     #[test]
     fn test_max_accounts() {
-        let signatures = vec![Pubkey::default(); usize::from(MAX_STATIC_ACCOUNTS_PER_PACKET)];
+        let signatures =
+            vec![Pubkey::default(); usize::from(LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET)];
         let bytes = bincode::serialize(&ShortVec(signatures)).unwrap();
         let mut offset = 0;
         let frame = StaticAccountKeysFrame::try_new(&bytes, &mut offset).unwrap();
@@ -82,7 +85,8 @@ mod tests {
 
     #[test]
     fn test_too_many_accounts() {
-        let signatures = vec![Pubkey::default(); usize::from(MAX_STATIC_ACCOUNTS_PER_PACKET) + 1];
+        let signatures =
+            vec![Pubkey::default(); usize::from(LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET) + 1];
         let bytes = bincode::serialize(&ShortVec(signatures)).unwrap();
         let mut offset = 0;
         assert!(StaticAccountKeysFrame::try_new(&bytes, &mut offset).is_err());
```
