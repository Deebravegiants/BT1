# [?] Merge pull request from GHSA-5233-j5mj-qxww

## Summary
Severity: Unknown
Chain: Solana
Component: metaplex-foundation/mpl-token-metadata
Published: 2023-02-08
Source: https://github.com/metaplex-foundation/mpl-token-metadata/commit/979ad38674a84049f6f8fa8a6a71e0195592053f
Type: security-commit

## Details
Merge pull request from GHSA-5233-j5mj-qxww

Co-Authored: Owlman <david@solshield.io>

## Patch
### token-metadata/program/src/assertions/misc.rs
```diff
@@ -23,6 +23,18 @@ pub fn assert_keys_equal(key1: &Pubkey, key2: &Pubkey) -> Result<(), ProgramErro
     }
 }
 
+pub fn assert_keys_equal_with_error(
+    key1: &Pubkey,
+    key2: &Pubkey,
+    err: MetadataError,
+) -> Result<(), ProgramError> {
+    if !cmp_pubkeys(key1, key2) {
+        Err(err.into())
+    } else {
+        Ok(())
+    }
+}
+
 /// assert initialized account
 pub fn assert_initialized<T: Pack + IsInitialized>(
     account_info: &AccountInfo,
```

### token-metadata/program/src/processor/metadata/transfer.rs
```diff
@@ -183,6 +183,18 @@ fn transfer_v1(program_id: &Pubkey, ctx: Context<Transfer>, args: TransferArgs)
     msg!("deserializing metadata");
     let metadata = Metadata::from_account_info(ctx.accounts.metadata_info)?;
 
+    // Must be the actual current owner of the token where
+    // mint, token, owner and metadata accounts all match up.
+    assert_holding_amount(
+        &crate::ID,
+        ctx.accounts.token_owner_info,
+        ctx.accounts.metadata_info,
+        &metadata,
+        ctx.accounts.mint_info,
+        ctx.accounts.token_info,
+        amount,
+    )?;
+
     let token_transfer_params: TokenTransferParams = TokenTransferParams {
         mint: ctx.accounts.mint_info.clone(),
         source: ctx.accounts.token_info.clone(),
@@ -246,18 +258,6 @@ fn transfer_v1(program_id: &Pubkey, ctx: Context<Transfer>, args: TransferArgs)
             // PDA to go around this restriction for cases where they are passing through a proper system wallet
             // signer via an invoke call.
             is_wallet_to_wallet = !is_cpi && wallets_are_system_program_owned;
-
-            // Must be the actual current owner of the token where
-            // mint, token, owner and metadata accounts all match up.
-            assert_holding_amount(
-                &crate::ID,
-                ctx.accounts.token_owner_info,
-                ctx.accounts.metadata_info,
-                &metadata,
-                ctx.accounts.mint_info,
-                ctx.accounts.token_info,
-                amount,
-            )?;
         }
         AuthorityType::Delegate => {
             // the delegate has already being validated, but we need to validate
```

### token-metadata/program/tests/transfer.rs
```diff
@@ -776,6 +776,109 @@ mod auth_rules_transfer {
         assert_eq!(authority_ata_account.amount, 1);
     }
 
+    #[tokio::test]
+    async fn transfer_delegate_wrong_metadata() {
+        // Tests a delegate transferring from a system wallet to a PDA and vice versa.
+        let mut program_test = ProgramTest::new("mpl_token_metadata", mpl_token_metadata::ID, None);
+        program_test.add_program("mpl_token_auth_rules", mpl_token_auth_rules::ID, None);
+        program_test.add_program("rooster", rooster::ID, None);
+        program_test.set_compute_max_units(400_000);
+        let mut context = program_test.start_with_context().await;
+
+        let payer = context.payer.dirty_clone();
+
+        // Create rule-set for the transfer; this has the Rooster program in the allowlist.
+        let (rule_set, mut auth_data) =
+            create_default_metaplex_rule_set(&mut context, payer, false).await;
+
+        // Create NFT for transfer tests.
+        let mut nft = DigitalAsset::new();
+        nft.create_and_mint(
+            &mut context,
+            TokenStandard::ProgrammableNonFungible,
+            Some(rule_set),
+            Some(auth_data.clone()),
+            1,
+        )
+        .await
+        .unwrap();
+
+        let mut nft_naughty = DigitalAsset::new();
+        nft_naughty
+            .create_and_mint(
+                &mut context,
+                TokenStandard::ProgrammableNonFungible,
+                None,
+                None,
+                1,
+            )
+            .await
+            .unwrap();
+
+        let transfer_amount = 1;
+
+        // Create a transfer delegate
+        let payer = context.payer.dirty_clone();
+        let delegate = Keypair::new();
+        airdrop(&mut context, &delegate.pubkey(), LAMPORTS_PER_SOL)
+            .await
+            .unwrap();
+
+        let delegate_args = DelegateArgs::TransferV1 {
+            amount: transfer_amount,
+            authorization_data: None,
+        };
+
+        nft.delegate(&mut context, payer, delegate.pubkey(), delegate_args)
+            .await
+            .unwrap();
+
+        let delegate_role = nft
+            .get_token_delegate_role(&mut context, &nft.token.unwrap())
+            .await;
+
+        assert_eq!(delegate_role, Some(TokenDelegateRole::Transfer));
+
+        // Set up the PDA account.
+        let authority = context.payer.dirty_clone();
+        let rooster_manager = RoosterManager::init(&mut context, authority).await.unwrap();
+
+        let authority = context.payer.dirty_clone();
+
+        // Update auth data payload with the seeds of the PDA we're
+        // transferring to.
+        let seeds = SeedsVec {
+            seeds: vec![
+                String::from("rooster").as_bytes().to_vec(),
+                authority.pubkey().as_ref().to_vec(),
+            ],
+        };
+
+        auth_data.payload.insert(
+            PayloadKey::DestinationSeeds.to_string(),
+            PayloadType::Seeds(seeds),
+        );
+
+        let args = TransferArgs::V1 {
+            authorization_data: Some(auth_data.clone()),
+            amount: transfer_amount,
+        };
+
+        let params = TransferFromParams {
+            context: &mut context,
+            authority: &delegate,
+            source_owner: &authority.pubkey(),
+            destination_owner: rooster_manager.pda(),
+            destination_token: None,
+            authorization_rules: Some(rule_set),
+            payer: &authority,
+            args: args.clone(),
+        };
+        nft.metadata = nft_naughty.metadata;
+        let err = nft.transfer_from(params).await.unwrap_err();
+        assert_custom_error_ix!(2, err, MetadataError::MintMismatch);
+    }
+
     #[tokio::test]
     async fn sale_delegate() {
         // Tests a delegate transferring from a system wallet to a PDA and vice versa.
```
