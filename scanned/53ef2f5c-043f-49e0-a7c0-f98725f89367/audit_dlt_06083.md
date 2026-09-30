# [?] Merge pull request from GHSA-8r76-fr72-j32w

## Summary
Severity: Unknown
Chain: Solana
Component: metaplex-foundation/mpl-token-metadata
Published: 2022-12-10
Source: https://github.com/metaplex-foundation/mpl-token-metadata/commit/277bd209c33a05e0cc73d0f7e52cfc1391cb853a
Type: security-commit

## Details
Merge pull request from GHSA-8r76-fr72-j32w

* adds bubblegum fix for creator verification

* adds compression module

* Fix assert collection update

* puts fix back to account

* bgum test fixes

* ensure that creator verification works

* Modify bubblegum signer logic

* bump version of bgum

* linting

* Reported by David of SolShield

Co-authored-by: austbot <me@austbot.com>
Co-authored-by: febo <febo@metaplex.com>
Co-authored-by: metamania01 <davidmnstr01@gmail.com>
Co-authored-by: Austin Adams <austbot@users.noreply.github.com>

## Patch
### token-metadata/program/src/assertions/collection.rs
```diff
@@ -10,23 +10,37 @@ use crate::{
     },
 };
 
+/// Checks whether the collection update is allowed or not based on the `verified` status.
 pub fn assert_collection_update_is_valid(
     edition: bool,
     existing: &Option<Collection>,
     incoming: &Option<Collection>,
 ) -> Result<(), ProgramError> {
-    let is_incoming_verified_true = incoming.is_some() && incoming.as_ref().unwrap().verified;
+    let is_incoming_verified = if let Some(status) = incoming {
+        status.verified
+    } else {
+        false
+    };
 
-    // If incoming verified is true. Confirm incoming and existing are identical
-    let is_incoming_data_valid = !is_incoming_verified_true
-        || (existing.is_some()
-            && incoming.as_ref().unwrap().verified == existing.as_ref().unwrap().verified
-            && incoming.as_ref().unwrap().key == existing.as_ref().unwrap().key);
+    let is_existing_verified = if let Some(status) = existing {
+        status.verified
+    } else {
+        false
+    };
 
-    if !is_incoming_data_valid && !edition {
-        // Never allow a collection to be verified outside of verify_collection instruction
+    let valid_update = if is_incoming_verified {
+        // verified: can only update if the details match
+        is_existing_verified && (existing.as_ref().unwrap().key == incoming.as_ref().unwrap().key)
+    } else {
+        // unverified: can only update if existing is unverified
+        !is_existing_verified
+    };
+
+    // overrule: if we are dealing with an edition
+    if !valid_update && !edition {
         return Err(MetadataError::CollectionCannotBeVerifiedInThisInstruction.into());
     }
+
     Ok(())
 }
 
@@ -129,3 +143,119 @@ pub fn assert_master_edition(
     }
     Ok(())
 }
+
+#[cfg(test)]
+pub mod tests {
+    use super::*;
+
+    #[test]
+    fn test_assert_collection_update_is_valid() {
+        let key_1 = Pubkey::new_unique();
+        let key_2 = Pubkey::new_unique();
+
+        // collection 1
+
+        let collection_key1_false = Collection {
+            key: key_1,
+            verified: false,
+        };
+
+        let collection_key1_true = Collection {
+            key: key_1,
+            verified: true,
+        };
+
+        // collection 2
+
+        let collection_key2_false = Collection {
+            key: key_2,
+            verified: false,
+        };
+
+        let collection_key2_true = Collection {
+            key: key_2,
+            verified: true,
+        };
+
+        // [OK] "unverified" same collection details
+
+        assert_collection_update_is_valid(
+            false,
+            &Some(collection_key1_false.clone()),
+            &Some(collection_key1_false.clone()),
+        )
+        .unwrap();
+
+        // [OK] "verified" same collection details
+
+        assert_collection_update_is_valid(
+            false,
+            &Some(collection_key1_true.clone()),
+            &Some(collection_key1_true.clone()),
+        )
+        .unwrap();
+
+        // [ERROR] "unverify" collection
+
+        assert_collection_update_is_valid(
+            false,
+            &Some(collection_key1_true.clone()),
+            &Some(collection_key1_false.clone()),
+        )
+        .unwrap_err();
+
+        // [ERROR] "verify" collection
+
+        assert_collection_update_is_valid(
+            false,
+            &Some(collection_key1_false.clone()),
+            &Some(collection_key1_true.clone()),
+        )
+        .unwrap_err();
+
+        // [OK] "unverified" update collection details
+
+        assert_collection_update_is_valid(
+            false,
+            &Some(collection_key1_false.clone()),
+            &Some(collection_key2_false.clone()),
+        )
+        .unwrap();
+
+        // [ERROR] "verified" update collection details
+
+        assert_collection_update_is_valid(
+            false,
+            &Some(collection_key1_false),
+            &Some(collection_key2_true.clone()),
+        )
+        .unwrap_err();
+
+        // [ERROR] "verified" update collection details
+
+        assert_collection_update_is_valid(
+            false,
+            &Some(collection_key1_true.clone()),
+            &Some(collection_key2_false),
+        )
+        .unwrap_err();
+
+        // [ERROR] "verified" update collection details
+
+        assert_collection_update_is_valid(
+            false,
+            &Some(collection_key1_true.clone()),
+            &Some(collection_key2_true.clone()),
+        )
+        .unwrap_err();
+
+        // [OK] "edition" override
+
+        assert_collection_update_is_valid(
+            true,
+            &Some(collection_key1_true),
+            &Some(collection_key2_true),
+        )
+        .unwrap();
+    }
+}
```

### token-metadata/program/src/pda.rs
```diff
@@ -25,6 +25,7 @@ pub fn find_edition_account(mint: &Pubkey, edition_number: String) -> (Pubkey, u
         &crate::id(),
     )
 }
+
 pub fn find_master_edition_account(mint: &Pubkey) -> (Pubkey, u8) {
     Pubkey::find_program_address(
         &[
```

### token-metadata/program/src/utils/compression.rs
```diff
@@ -0,0 +1,27 @@
+use mpl_utils::cmp_pubkeys;
+use solana_program::{account_info::AccountInfo, pubkey, pubkey::Pubkey};
+
+use super::*;
+pub const BUBBLEGUM_PROGRAM_ADDRESS: Pubkey =
+    pubkey!("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY");
+
+pub const BUBBLEGUM_SIGNER: Pubkey = pubkey!("4ewWZC5gT6TGpm5LZNDs9wVonfUT2q5PP5sc9kVbwMAK");
+
+// This flag activates certain program authority features of the Bubblegum program.
+pub const BUBBLEGUM_ACTIVATED: bool = true;
+
+pub fn find_compression_mint_authority(mint: &Pubkey) -> (Pubkey, u8) {
+    let seeds = &[mint.as_ref()];
+    Pubkey::find_program_address(seeds, &BUBBLEGUM_PROGRAM_ADDRESS)
+}
+
+pub fn is_decompression(mint: &AccountInfo, mint_authority_info: &AccountInfo) -> bool {
+    if BUBBLEGUM_ACTIVATED
+        && mint_authority_info.is_signer
+        && cmp_pubkeys(mint_authority_info.owner, &BUBBLEGUM_PROGRAM_ADDRESS)
+    {
+        let (expected, _) = find_compression_mint_authority(mint.key);
+        return cmp_pubkeys(mint_authority_info.key, &expected);
+    }
+    false
+}
```

### token-metadata/program/src/utils/metadata.rs
```diff
@@ -5,7 +5,7 @@ use solana_program::{
     pubkey::Pubkey,
 };
 
-use super::*;
+use super::{compression::is_decompression, *};
 use crate::{
     assertions::{
         assert_mint_authority_matches_mint, assert_owned_by,
@@ -33,13 +33,6 @@ pub const SEED_AUTHORITY: Pubkey = Pubkey::new_from_array([
 
 // This allows the Bubblegum program to add verified creators since they were verified as part of
 // the Bubblegum program.
-pub const BUBBLEGUM_PROGRAM_ADDRESS: Pubkey =
-    pubkey!("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY");
-
-pub const BUBBLEGUM_SIGNER: Pubkey = pubkey!("4ewWZC5gT6TGpm5LZNDs9wVonfUT2q5PP5sc9kVbwMAK");
-
-// This flag activates certain program authority features of the Bubblegum program.
-pub const BUBBLEGUM_ACTIVATED: bool = true;
 
 pub struct CreateMetadataAccountsLogicArgs<'a> {
     pub metadata_account_info: &'a AccountInfo<'a>,
@@ -123,14 +116,9 @@ pub fn process_create_metadata_accounts_logic(
 
     // This allows the Bubblegum program to create metadata with verified creators since they were
     // verified already by the Bubblegum program.
-    let allow_direct_creator_writes = if BUBBLEGUM_ACTIVATED
-        && mint_authority_info.owner == &BUBBLEGUM_PROGRAM_ADDRESS
-        && mint_authority_info.is_signer
-    {
-        true
-    } else {
-        allow_direct_creator_writes
-    };
+    // 
+    let allow_direct_creator_writes =
+        allow_direct_creator_writes || is_decompression(mint_info, mint_authority_info);
 
     assert_data_valid(
         &compatible_data,
```

### token-metadata/program/src/utils/mod.rs
```diff
@@ -1,8 +1,10 @@
 pub(crate) mod collection;
+pub(crate) mod compression;
 pub(crate) mod master_edition;
 pub(crate) mod metadata;
 
 pub use collection::*;
+pub use compression::*;
 pub use master_edition::*;
 pub use metadata::*;
 use mpl_utils::token::{get_mint_decimals, get_mint_freeze_authority, get_mint_supply};
```

### token-metadata/program/tests/create_metadata_account.rs
```diff
@@ -5,10 +5,10 @@ use mpl_token_metadata::{
     error::MetadataError,
     id, instruction,
     state::{Creator, Key, UseMethod, Uses, MAX_NAME_LENGTH, MAX_SYMBOL_LENGTH, MAX_URI_LENGTH},
-    utils::puffed_out_string,
+    utils::{puffed_out_string, BUBBLEGUM_PROGRAM_ADDRESS},
 };
 use num_traits::FromPrimitive;
-use solana_program::pubkey::Pubkey;
+use solana_program::{pubkey::Pubkey, system_instruction::assign};
 use solana_program_test::*;
 use solana_sdk::{
     instruction::InstructionError,
@@ -574,4 +574,112 @@ mod create_meta_accounts {
         })
         .await;
     }
+
+    #[tokio::test]
+    async fn fail_bubblegum_owner() {
+        let mut context = &mut program_test().start_with_context().await;
+        let test_metadata = Metadata::new();
+        let name = "Test".to_string();
+        let symbol = "TST".to_string();
+        let uri = "uri".to_string();
+        let mint_authority = Keypair::new();
+
+        airdrop(context, &mint_authority.pubkey(), 1_000_000)
+            .await
+            .unwrap();
+        let uses = Some(Uses {
+            total: 1,
+            remaining: 1,
+            use_method: UseMethod::Single,
+        });
+
+        create_mint(
+            context,
+            &test_metadata.mint,
+            &mint_authority.pubkey(),
+            Some(&context.payer.pubkey()),
+            0,
+        )
+        .await
+        .unwrap();
+
+        create_token_account(
+            context,
+            &test_metadata.token,
+            &test_metadata.mint.pubkey(),
+            &context.payer.pubkey(),
+        )
+        .await
+        .unwrap();
+
+        mint_tokens(
+            context,
+            &test_metadata.mint.pubkey(),
+            &test_metadata.token.pubkey(),
+            1,
+            &mint_authority.pubkey(),
+            Some(&mint_authority),
+            // None
+        )
+        .await
+        .unwrap();
+
+        // Assign to bubblegum program and stuff
+        let assign_ix = assign(&mint_authority.pubkey(), &BUBBLEGUM_PROGRAM_ADDRESS);
+        let assign_tx = Transaction::new_signed_with_payer(
+            &[assign_ix],
+            Some(&context.payer.pubkey()),
+            &[&context.payer, &mint_authority],
+            context.last_blockhash,
+        );
+
+        context
+            .banks_client
+            .process_transaction(assign_tx)
+            .await
+            .unwrap();
+
+        let mint_authority_account = get_account(context, &mint_authority.pubkey()).await;
+        assert_eq!(mint_authority_account.owner, BUBBLEGUM_PROGRAM_ADDRESS);
+        let mint_account = get_mint(context, &test_metadata.mint.pubkey()).await;
+        assert_eq!(
+            mint_account.mint_authority.unwrap(),
+            mint_authority.pubkey()
+        );
+
+        let random_verified_creator = Creator {
+            address: Pubkey::new_unique(),
+            share: 100,
+            verified: true,
+        };
+
+        let create_tx = Transaction::new_signed_with_payer(
+            &[instruction::create_metadata_accounts_v2(
+                id(),
+                test_metadata.pubkey,
+                test_metadata.mint.pubkey(),
+                mint_authority.pubkey(),
+                context.payer.pubkey(),
+                context.payer.pubkey(),
+                name,
+                symbol,
+                uri,
+                Some(vec![random_verified_creator.clone()]),
+                10,
+                true,
+                true,
+                None,
+                uses.to_owned(),
+            )],
+            Some(&context.payer.pubkey()),
+            &[&context.payer, &mint_authority],
+            context.last_blockhash,
+        );
+        let error = context
+            .banks_client
+            .process_transaction(create_tx)
+            .await
+            .unwrap_err();
+        assert_custom_error!(error, MetadataError::CannotVerifyAnotherCreator);
+    }
 }
```

### token-metadata/program/tests/mint_new_edition_from_master_edition_via_token.rs
```diff
@@ -5,11 +5,13 @@ use borsh::BorshSerialize;
 use mpl_token_metadata::{
     error::MetadataError,
     id, instruction,
-    state::{Key, MAX_MASTER_EDITION_LEN},
+    state::{Creator, Key, MAX_MASTER_EDITION_LEN},
 };
+use mpl_token_metadata::{instruction::sign_metadata, state::Collection};
 use num_traits::FromPrimitive;
 use solana_program_test::*;
 use solana_sdk::{
+    account::AccountSharedData,
     instruction::InstructionError,
     signature::{Keypair, Signer},
     transaction::{Transaction, TransactionError},
@@ -19,13 +21,14 @@ use utils::*;
 // NOTE: these tests depend on the token-vault program having been compiled
 // via (cd ../../token-vault/program/ && cargo build-bpf)
 mod mint_new_edition_from_master_edition_via_token {
-    use mpl_token_metadata::state::Collection;
-    use solana_sdk::account::AccountSharedData;
+
+    use solana_program::native_token::LAMPORTS_PER_SOL;
 
     use super::*;
     #[tokio::test]
     async fn success() {
         let mut context = program_test().start_with_context().await;
+        let payer_key = context.payer.pubkey().clone();
         let test_metadata = Metadata::new();
         let test_master_edition = MasterEditionV2::new(&test_metadata);
         let test_edition_marker = EditionMarker::new(&test_metadata, &test_master_edition, 1);
@@ -36,7 +39,11 @@ mod mint_new_edition_from_master_edition_via_token {
                 "Test".to_string(),
                 "TST".to_string(),
                 "uri".to_string(),
-                None,
+                Some(vec![Creator {
+                    address: payer_key,
+                    verified: true,
+                    share: 100,
+                }]),
                 10,
                 false,
                 0,
@@ -61,6 +68,13 @@ mod mint_new_edition_from_master_edition_via_token {
     async fn success_v2() {
         let mut context = program_test().start_with_context().await;
         let test_metadata = Metadata::new();
+        let payer_key = context.payer.pubkey().clone();
+        let creator = Keypair::new();
+
+        let creator_pub = creator.pubkey().clone();
+        airdrop(&mut context, &creator_pub.clone(), 3 * LAMPORTS_PER_SOL)
+            .await
+            .unwrap();
         let test_master_edition = MasterEditionV2::new(&test_metadata);
         let test_collection = Metadata::new();
         test_collection
@@ -78,7 +92,11 @@ mod mint_new_edition_from_master_edition_via_token {
                 "Test".to_string(),
                 "TST".to_string(),
                 "uri".to_string(),
-                None,
+                Some(vec![Creator {
+                    address: creator_pub.clone(),
+                    verified: false,
+                    share: 100,
+                }]),
                 10,
                 false,
                 Some(Collection {
@@ -94,6 +112,20 @@ mod mint_new_edition_from_master_edition_via_token {
             .create(&mut context, Some(10))
             .await
             .unwrap();
+
+        let tx = Transaction::new_signed_with_payer(
+            &[instruction::sign_metadata(
+                mpl_token_metadata::id(),
+                test_metadata.pubkey,
+                creator_pub,
+            )]
+            .as_ref(),
+            Some(&creator_pub),
+            &[&creator],
+            context.last_blockhash,
+        );
+        let result = context.banks_client.process_transaction(tx).await;
+
         let kpbytes = &context.payer;
         let kp = Keypair::from_bytes(&kpbytes.to_bytes()).unwrap();
         test_metadata
```
