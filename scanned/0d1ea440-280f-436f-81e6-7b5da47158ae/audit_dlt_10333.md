# [?] Merge pull request from GHSA-24mm-x9x4-83rc

## Summary
Severity: Unknown
Chain: Solana
Component: metaplex-foundation/mpl-token-metadata
Published: 2022-05-04
Source: https://github.com/metaplex-foundation/mpl-token-metadata/commit/ff96466a69f4403e6f4f8f0d0af04b7c4ab2ca4d
Type: security-commit

## Details
Merge pull request from GHSA-24mm-x9x4-83rc

* Revoke as delegate

* Bumping token-metadata cargo version

## Patch
### token-metadata/Cargo.lock
```diff
@@ -1490,7 +1490,7 @@ dependencies = [
 
 [[package]]
 name = "mpl-token-metadata"
-version = "1.2.8"
+version = "1.2.9"
 dependencies = [
  "arrayref",
  "borsh",
```

### token-metadata/program/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "mpl-token-metadata"
-version = "1.2.8"
+version = "1.2.9"
 description = "Metaplex Metadata"
 authors = ["Metaplex Developers <dev@metaplex.com>"]
 repository = "https://github.com/metaplex-foundation/metaplex-program-library"
```

### token-metadata/program/src/error.rs
```diff
@@ -43,7 +43,7 @@ pub enum MetadataError {
     #[error("Update Authority given does not match")]
     UpdateAuthorityIncorrect,
 
-    /// Update Authority needs to be signer to update  metadata
+    /// Update Authority needs to be signer to update metadata
     #[error("Update Authority needs to be signer to update metadata")]
     UpdateAuthorityIsNotSigner,
 
@@ -382,6 +382,10 @@ pub enum MetadataError {
 
     #[error("Invalid User")]
     InvalidUser,
+
+    /// Revoke Collection Authority signer is incorrect
+    #[error("Revoke Collection Authority signer is incorrect")]
+    RevokeCollectionAuthoritySignerIncorrect,
 }
 
 impl PrintProgramError for MetadataError {
```

### token-metadata/program/src/instruction.rs
```diff
@@ -363,9 +363,10 @@ pub enum MetadataInstruction {
 
     /// Revoke account to call [verify_collection] on this NFT.
     #[account(0, writable, name="collection_authority_record", desc="Collection Authority Record PDA")]
-    #[account(1, signer, writable, name="update_authority", desc="Update Authority of Collection NFT")]
-    #[account(2, name="metadata", desc="Metadata account")]
-    #[account(3, name="mint", desc="Mint of Metadata")]
+    #[account(1, signer, writable, name="delegate_authority", desc="Delegated Collection Authority")]
+    #[account(2, signer, writable, name="revoke_authority", desc="Update Authority, or Delegated Authority, of Collection NFT")]
+    #[account(3, name="metadata", desc="Metadata account")]
+    #[account(4, name="mint", desc="Mint of Metadata")]
     RevokeCollectionAuthority,
 
     /// Allows the same Update Authority (Or Delegated Authority) on an NFT and Collection to perform [update_metadata_accounts_v2] 
@@ -1118,15 +1119,15 @@ pub fn approve_collection_authority(
 ///
 ///   0. `[writable]` Collection Authority Record PDA
 ///   1. `[writable]` The Authority that was delegated to
-///   2. `[signer]` The Original Update Authority
+///   2. `[signer]` The Original Update Authority or Delegated Authority
 ///   2. `[]` Metadata account
 ///   3. `[]` Mint of Metadata
 #[allow(clippy::too_many_arguments)]
 pub fn revoke_collection_authority(
     program_id: Pubkey,
     collection_authority_record: Pubkey,
     delegate_authority: Pubkey,
-    update_authority: Pubkey,
+    revoke_authority: Pubkey,
     metadata: Pubkey,
     mint: Pubkey,
 ) -> Instruction {
@@ -1135,7 +1136,7 @@ pub fn revoke_collection_authority(
         accounts: vec![
             AccountMeta::new(collection_authority_record, false),
             AccountMeta::new_readonly(delegate_authority, false),
-            AccountMeta::new(update_authority, true),
+            AccountMeta::new(revoke_authority, true),
             AccountMeta::new_readonly(metadata, false),
             AccountMeta::new_readonly(mint, false),
         ],
```

### token-metadata/program/src/processor.rs
```diff
@@ -1167,15 +1167,17 @@ pub fn process_revoke_collection_authority(
     let account_info_iter = &mut accounts.iter();
     let collection_authority_record = next_account_info(account_info_iter)?;
     let delegate_authority = next_account_info(account_info_iter)?;
-    let update_authority = next_account_info(account_info_iter)?;
+    let revoke_authority = next_account_info(account_info_iter)?;
     let metadata_info = next_account_info(account_info_iter)?;
     let mint_info = next_account_info(account_info_iter)?;
     let metadata = Metadata::from_account_info(metadata_info)?;
     assert_owned_by(metadata_info, program_id)?;
     assert_owned_by(mint_info, &spl_token::id())?;
-    assert_signer(update_authority)?;
-    if metadata.update_authority != *update_authority.key {
-        return Err(MetadataError::UpdateAuthorityIncorrect.into());
+    assert_signer(revoke_authority)?;
+    if metadata.update_authority != *revoke_authority.key
+        && *delegate_authority.key != *revoke_authority.key
+    {
+        return Err(MetadataError::RevokeCollectionAuthoritySignerIncorrect.into());
     }
     if metadata.mint != *mint_info.key {
         return Err(MetadataError::MintMismatch.into());
@@ -1192,7 +1194,7 @@ pub fn process_revoke_collection_authority(
     )?;
     let lamports = collection_authority_record.lamports();
     **collection_authority_record.try_borrow_mut_lamports()? = 0;
-    **update_authority.try_borrow_mut_lamports()? = update_authority
+    **revoke_authority.try_borrow_mut_lamports()? = revoke_authority
         .lamports()
         .checked_add(lamports)
         .ok_or(MetadataError::NumericalOverflowError)?;
```

### token-metadata/program/tests/verify_collection.rs
```diff
@@ -873,6 +873,130 @@ mod verify_collection {
         assert!(!metadata_after_unverify.collection.unwrap().verified);
     }
 
+    #[tokio::test]
+    async fn success_set_and_verify_collection_with_authority_and_revoke_as_delegate() {
+        let mut context = program_test().start_with_context().await;
+        let new_collection_authority = Keypair::new();
+        airdrop(&mut context, &new_collection_authority.pubkey(), 10000000)
+            .await
+            .unwrap();
+
+        let test_collection = Metadata::new();
+        test_collection
+            .create_v2(
+                &mut context,
+                "Test".to_string(),
+                "TST".to_string(),
+                "uri".to_string(),
+                None,
+                10,
+                false,
+                None,
+                None,
+                None,
+            )
+            .await
+            .unwrap();
+        let collection_master_edition_account = MasterEditionV2::new(&test_collection);
+        collection_master_edition_account
+            .create_v3(&mut context, Some(0))
+            .await
+            .unwrap();
+
+        let name = "Test".to_string();
+        let symbol = "TST".to_string();
+        let uri = "uri".to_string();
+        let test_metadata = Metadata::new();
+        test_metadata
+            .create_v2(
+                &mut context,
+                name,
+                symbol,
+                uri,
+                None,
+                10,
+                false,
+                None,
+                None,
+                None,
+            )
+            .await
+            .unwrap();
+
+        let metadata = test_metadata.get_data(&mut context).await;
+        assert!(metadata.collection.is_none());
+        let update_authority = context.payer.pubkey();
+        let (record, _) = find_collection_authority_account(
+            &test_collection.mint.pubkey(),
+            &new_collection_authority.pubkey(),
+        );
+        let ix = mpl_token_metadata::instruction::approve_collection_authority(
+            mpl_token_metadata::id(),
+            record,
+            new_collection_authority.pubkey(),
+            update_authority,
+            context.payer.pubkey(),
+            test_collection.pubkey,
+            test_collection.mint.pubkey(),
+        );
+
+        let tx = Transaction::new_signed_with_payer(
+            &[ix],
+            Some(&context.payer.pubkey()),
+            &[&context.payer],
+            context.last_blockhash,
+        );
+
+        context.banks_client.process_transaction(tx).await.unwrap();
+
+        let record_account = get_account(&mut context, &record).await;
+        let record_data: CollectionAuthorityRecord =
+            try_from_slice_unchecked(&record_account.data).unwrap();
+        assert_eq!(record_data.key, Key::CollectionAuthorityRecord);
+
+        test_metadata
+            .set_and_verify_collection(
+                &mut context,
+                test_collection.pubkey,
+                &new_collection_authority,
+                update_authority,
+                test_collection.mint.pubkey(),
+                collection_master_edition_account.pubkey,
+                Some(record),
+            )
+            .await
+            .unwrap();
+
+        let metadata_after = test_metadata.get_data(&mut context).await;
+        assert_eq!(
+            metadata_after.collection.to_owned().unwrap().key,
+            test_collection.mint.pubkey()
+        );
+        assert!(metadata_after.collection.unwrap().verified);
+
+        let ix_revoke = mpl_token_metadata::instruction::revoke_collection_authority(
+            mpl_token_metadata::id(),
+            record,
+            new_collection_authority.pubkey(),
+            new_collection_authority.pubkey(),
+            test_collection.pubkey,
+            test_collection.mint.pubkey(),
+        );
+
+        let tx_revoke = Transaction::new_signed_with_payer(
+            &[ix_revoke],
+            Some(&new_collection_authority.pubkey()),
+            &[&new_collection_authority],
+            context.last_blockhash,
+        );
+
+        context
+            .banks_client
+            .process_transaction(tx_revoke)
+            .await
+            .unwrap();
+    }
+
     #[tokio::test]
     async fn fail_verify_collection_with_authority() {
         let mut context = program_test().start_with_context().await;
@@ -1005,8 +1129,150 @@ mod verify_collection {
             )
             .await
             .unwrap_err();
+
         assert_custom_error!(err, MetadataError::InvalidCollectionUpdateAuthority);
         let metadata_after = test_metadata.get_data(&mut context).await;
         assert!(!metadata_after.collection.unwrap().verified);
     }
+
+    #[tokio::test]
+    async fn fail_set_and_verify_collection_with_authority_and_revoke_as_wrong_signer() {
+        let mut context = program_test().start_with_context().await;
+        let new_collection_authority = Keypair::new();
+        let incorrect_revoke_authority = Keypair::new();
+        airdrop(&mut context, &incorrect_revoke_authority.pubkey(), 10000000)
+            .await
+            .unwrap();
+
+        let test_collection = Metadata::new();
+        test_collection
+            .create_v2(
+                &mut context,
+                "Test".to_string(),
+                "TST".to_string(),
+                "uri".to_string(),
+                None,
+                10,
+                false,
+                None,
+                None,
+                None,
+            )
+            .await
+            .unwrap();
+        let collection_master_edition_account = MasterEditionV2::new(&test_collection);
+        collection_master_edition_account
+            .create_v3(&mut context, Some(0))
+            .await
+            .unwrap();
+
+        let name = "Test".to_string();
+        let symbol = "TST".to_string();
+        let uri = "uri".to_string();
+        let test_metadata = Metadata::new();
+        test_metadata
+            .create_v2(
+                &mut context,
+                name,
+                symbol,
+                uri,
+                None,
+                10,
+                false,
+                None,
+                None,
+                None,
+            )
+            .await
+            .unwrap();
+
+        let metadata = test_metadata.get_data(&mut context).await;
+        assert!(metadata.collection.is_none());
+        let update_authority = context.payer.pubkey();
+        let (record, _) = find_collection_authority_account(
+            &test_collection.mint.pubkey(),
+            &new_collection_authority.pubkey(),
+        );
+        let ix = mpl_token_metadata::instruction::approve_collection_authority(
+            mpl_token_metadata::id(),
+            record,
+            new_collection_authority.pubkey(),
+            update_authority,
+            context.payer.pubkey(),
+            test_collection.pubkey,
+            test_collection.mint.pubkey(),
+        );
+
+        let tx = Transaction::new_signed_with_payer(
+            &[ix],
+            Some(&context.payer.pubkey()),
+            &[&context.payer],
+            context.last_blockhash,
+        );
+
+        context.banks_client.process_transaction(tx).await.unwrap();
+
+        let record_account = get_account(&mut context, &record).await;
+        let record_data: CollectionAuthorityRecord =
+            try_from_slice_unchecked(&record_account.data).unwrap();
+        assert_eq!(record_data.key, Key::CollectionAuthorityRecord);
+
+        test_metadata
+            .set_and_verify_collection(
+                &mut context,
+                test_collection.pubkey,
+                &new_collection_authority,
+                update_authority,
+                test_collection.mint.pubkey(),
+                collection_master_edition_account.pubkey,
+                Some(record),
+            )
+            .await
+            .unwrap();
+
+        let metadata_after = test_metadata.get_data(&mut context).await;
+        assert_eq!(
+            metadata_after.collection.to_owned().unwrap().key,
+            test_collection.mint.pubkey()
+        );
+        assert!(metadata_after.collection.unwrap().verified);
+
+        test_metadata
+            .unverify_collection(
+                &mut context,
+                test_collection.pubkey,
+                &new_collection_authority,
+                test_collection.mint.pubkey(),
+                collection_master_edition_account.pubkey,
+                Some(record),
+            )
+            .await
+            .unwrap();
+        let metadata_after_unverify = test_metadata.get_data(&mut context).await;
+        assert!(!metadata_after_unverify.collection.unwrap().verified);
+
+        let ix_revoke = mpl_token_metadata::instruction::revoke_collection_authority(
+            mpl_token_metadata::id(),
+            record,
+            new_collection_authority.pubkey(),
+            incorrect_revoke_authority.pubkey(),
+            test_collection.pubkey,
+            test_collection.mint.pubkey(),
+        );
+
+        let tx_revoke = Transaction::new_signed_with_payer(
+            &[ix_revoke],
+            Some(&incorrect_revoke_authority.pubkey()),
+            &[&incorrect_revoke_authority],
+            context.last_blockhash,
+        );
+
+        let err = context
+            .banks_client
+            .process_transaction(tx_revoke)
+            .await
+            .unwrap_err();
+
+        assert_custom_error!(err, MetadataError::RevokeCollectionAuthoritySignerIncorrect);
+    }
 }
```
