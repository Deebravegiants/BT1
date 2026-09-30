# [?] Merge pull request from GHSA-9fgp-8jc4-wmmw

## Summary
Severity: Unknown
Chain: Solana
Component: metaplex-foundation/mpl-token-metadata
Published: 2022-08-30
Source: https://github.com/metaplex-foundation/mpl-token-metadata/commit/0ccb431e206025c2570ae0a753bd113b425028a8
Type: security-commit

## Details
Merge pull request from GHSA-9fgp-8jc4-wmmw

## Patch
### token-metadata/program/src/assertions/collection.rs
```diff
@@ -48,6 +48,11 @@ pub fn assert_has_collection_authority(
     mint: &Pubkey,
     delegate_collection_authority_record: Option<&AccountInfo>,
 ) -> Result<(), ProgramError> {
+    // Mint is the correct one for the metadata account.
+    if collection_data.mint != *mint {
+        return Err(MetadataError::MintMismatch.into());
+    }
+
     if let Some(collection_authority_record) = delegate_collection_authority_record {
         let bump = assert_is_collection_delegated_authority(
             collection_authority_record,
```

### token-metadata/program/src/processor.rs
```diff
@@ -1854,7 +1854,11 @@ pub fn set_collection_size(
 
     // Owned by token-metadata program.
     assert_owned_by(parent_nft_metadata_account_info, program_id)?;
-    let mut metadata = Metadata::from_account_info(parent_nft_metadata_account_info)?;
+
+    // Mint owned by spl token program.
+    assert_owned_by(collection_mint_account_info, &spl_token::id())?;
+
+    let mut metadata: Metadata = Metadata::from_account_info(parent_nft_metadata_account_info)?;
 
     // Check that the update authority or delegate is a signer.
     if !collection_update_authority_account_info.is_signer {
```

### token-metadata/program/tests/set_collection_size.rs
```diff
@@ -677,6 +677,130 @@ async fn update_authority_not_a_signer_fails_with_delegated_collection_authority
     assert_custom_error!(err, MetadataError::UpdateAuthorityIsNotSigner);
 }
 
+#[tokio::test]
+async fn other_collection_delegate_cant_set_size() {
+    let mut context = program_test().start_with_context().await;
+
+    // Create a Collection Parent NFT with the CollectionDetails set to None
+    let collection_parent_nft = Metadata::new();
+    collection_parent_nft
+        .create_v3(
+            &mut context,
+            "Test".to_string(),
+            "TST".to_string(),
+            "uri".to_string(),
+            None,
+            10,
+            false,
+            None,
+            None,
+            None,
+            None,
+        )
+        .await
+        .unwrap();
+    let parent_master_edition_account = MasterEditionV2::new(&collection_parent_nft);
+    parent_master_edition_account
+        .create_v3(&mut context, Some(0))
+        .await
+        .unwrap();
+
+    // Create a Collection Parent NFT with the CollectionDetails set to None
+    let other_collection_parent_nft = Metadata::new();
+    other_collection_parent_nft
+        .create_v3(
+            &mut context,
+            "Test".to_string(),
+            "TST".to_string(),
+            "uri".to_string(),
+            None,
+            10,
+            false,
+            None,
+            None,
+            None,
+            None,
+        )
+        .await
+        .unwrap();
+    let other_parent_master_edition_account = MasterEditionV2::new(&other_collection_parent_nft);
+    other_parent_master_edition_account
+        .create_v3(&mut context, Some(0))
+        .await
+        .unwrap();
+
+    // NFT is created with context payer as the update authority so we need to update this so we don't automatically
+    // get the update authority to sign the transaction.
+    let first_update_authority = Keypair::new();
+    let other_update_authority = Keypair::new();
+    let delegate_authority = Keypair::new();
+
+    collection_parent_nft
+        .change_update_authority(&mut context, first_update_authority.pubkey())
+        .await
+        .unwrap();
+
+    other_collection_parent_nft
+        .change_update_authority(&mut context, other_update_authority.pubkey())
+        .await
+        .unwrap();
+
+    // Find authority record for other collection NFT.
+    let (record, _) = find_collection_authority_account(
+        &other_collection_parent_nft.mint.pubkey(),
+        &delegate_authority.pubkey(),
+    );
+
+    // Approve the delegate authority for the Other Collection NFT.
+    let ix = approve_collection_authority(
+        PROGRAM_ID,
+        record,
+        delegate_authority.pubkey(),
+        other_update_authority.pubkey(),
+        context.payer.pubkey(),
+        other_collection_parent_nft.pubkey,
+        other_collection_parent_nft.mint.pubkey(),
+    );
+
+    let tx = Transaction::new_signed_with_payer(
+        &[ix],
+        Some(&context.payer.pubkey()),
+        &[&context.payer, &other_update_authority],
+        context.last_blockhash,
+    );
+
+    context.banks_client.process_transaction(tx).await.unwrap();
+
+    let size = 1123;
+
+    // Set collection size on first Collection NFT using the Other delegate record and authority.
+    // This is subtle: we're using the *metadata* account of the first collection NFT, but the
+    // mint and delegate authority of the other collection NFT.
+    let ix = set_collection_size(
+        PROGRAM_ID,
+        collection_parent_nft.pubkey,
+        delegate_authority.pubkey(),
+        other_collection_parent_nft.mint.pubkey(),
+        Some(record),
+        size,
+    );
+
+    let tx = Transaction::new_signed_with_payer(
+        &[ix],
+        Some(&context.payer.pubkey()),
+        &[&context.payer, &delegate_authority],
+        context.last_blockhash,
+    );
+
+    let err = context
+        .banks_client
+        .process_transaction(tx)
+        .await
+        .unwrap_err();
+
+    assert_custom_error!(err, MetadataError::MintMismatch);
+}
+
 // Custom instruction to allow us to check attacks where there is not collection signer.
 fn set_collection_size_no_signer(
     program_id: Pubkey,
```
