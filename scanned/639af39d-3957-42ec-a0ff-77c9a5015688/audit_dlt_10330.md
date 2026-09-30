# [?] Merge pull request from GHSA-hgfm-qrw5-68qm

## Summary
Severity: Unknown
Chain: Solana
Component: metaplex-foundation/mpl-token-metadata
Published: 2023-03-14
Source: https://github.com/metaplex-foundation/mpl-token-metadata/commit/f3257d9cb9f1482731681cde303452cc90d14dc1
Type: security-commit

## Details
Merge pull request from GHSA-hgfm-qrw5-68qm

## Patch
### token-metadata/program/src/assertions/programmable.rs
```diff
@@ -7,8 +7,8 @@ use crate::{error::MetadataError, state::ProgrammableConfig};
 ///   1. authorization rules and data
 ///   2. edition account
 ///   3. rule_set passed in by the user to match that stored in the metadata
-pub(crate) fn assert_valid_authorization<'info>(
-    authorization_rules: Option<&AccountInfo<'info>>,
+pub(crate) fn assert_valid_authorization(
+    authorization_rules: Option<&AccountInfo>,
     config: &ProgrammableConfig,
 ) -> ProgramResult {
     let rules = match authorization_rules {
```

### token-metadata/program/src/error.rs
```diff
@@ -737,6 +737,10 @@ pub enum MetadataError {
     /// 186
     #[error("Missing collection master edition account")]
     MissingCollectionMasterEdition,
+
+    /// 187
+    #[error("Invalid token record account")]
+    InvalidTokenRecord,
 }
 
 impl PrintProgramError for MetadataError {
```

### token-metadata/program/src/processor/burn/burn.rs
```diff
@@ -1,6 +1,7 @@
 use super::*;
 
 use crate::{
+    pda::find_token_record_account,
     processor::burn::{fungible::burn_fungible, nonfungible_edition::burn_nonfungible_edition},
     state::{AuthorityRequest, AuthorityType, TokenDelegateRole, TokenRecord, TokenState},
     utils::{check_token_standard, thaw},
@@ -168,12 +169,22 @@ fn burn_v1(program_id: &Pubkey, ctx: Context<Burn>, args: BurnArgs) -> ProgramRe
         }
         TokenStandard::ProgrammableNonFungible => {
             // All the checks are the same as burning a NonFungible token
-            // except we also have to check the token state.
-            let token_record = ctx
-                .accounts
-                .token_record_info
-                .ok_or_else(|| MetadataError::MissingTokenRecord.into())
-                .and_then(TokenRecord::from_account_info)?;
+            // except we also have to check the token state and derivation.
+            let token_record = match ctx.accounts.token_record_info {
+                Some(token_record_info) => {
+                    let (pda_key, _) = find_token_record_account(
+                        ctx.accounts.mint_info.key,
+                        ctx.accounts.token_info.key,
+                    );
+
+                    if pda_key != *token_record_info.key {
+                        return Err(MetadataError::InvalidTokenRecord.into());
+                    }
+
+                    TokenRecord::from_account_info(token_record_info)?
+                }
+                None => return Err(MetadataError::MissingTokenRecord.into()),
+            };
 
             // Locked and Listed states cannot be burned.
             if token_record.state != TokenState::Unlocked {
```

### token-metadata/program/src/processor/mod.rs
```diff
@@ -423,9 +423,9 @@ pub fn try_get_optional_account_info<'a>(
 ///
 /// We need to determine if we are dealing with a pNFT metadata or not
 /// so we can restrict the available instructions.
-fn has_programmable_metadata<'a>(
+fn has_programmable_metadata(
     program_id: &Pubkey,
-    accounts: &'a [AccountInfo],
+    accounts: &[AccountInfo],
 ) -> Result<bool, ProgramError> {
     for account_info in accounts {
         // checks the account is owned by Token Metadata and it has data
@@ -449,7 +449,7 @@ fn has_programmable_metadata<'a>(
 }
 
 /// Checks if the instruction's accounts contain a locked pNFT.
-fn is_locked<'a>(program_id: &Pubkey, accounts: &'a [AccountInfo]) -> bool {
+fn is_locked(program_id: &Pubkey, accounts: &[AccountInfo]) -> bool {
     for account_info in accounts {
         // checks the account is owned by Token Metadata and it has data
         if account_info.owner == program_id && !account_info.data_is_empty() {
```

### token-metadata/program/tests/burn.rs
```diff
@@ -863,6 +863,88 @@ mod pnft {
 
         assert_custom_error!(err, MetadataError::DerivedKeyInvalid);
     }
+
+    #[tokio::test]
+    async fn owner_burn_token_record_must_match() {
+        // The token record must match the token.
+        let mut context = program_test().start_with_context().await;
+
+        let update_authority = context.payer.dirty_clone();
+        let owner = Keypair::new();
+        owner.airdrop(&mut context, 1_000_000).await.unwrap();
+
+        let mut da = DigitalAsset::new();
+        da.create_and_mint(
+            &mut context,
+            TokenStandard::ProgrammableNonFungible,
+            None,
+            None,
+            1,
+        )
+        .await
+        .unwrap();
+
+        // Create a second pNFT.
+        let mut da_other = DigitalAsset::new();
+        da_other
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
+        // Transfer to a new owner so the update authority is separate.
+        let args = TransferArgs::V1 {
+            authorization_data: None,
+            amount: 1,
+        };
+
+        da.transfer(TransferParams {
+            context: &mut context,
+            authority: &update_authority,
+            source_owner: &update_authority.pubkey(),
+            destination_owner: owner.pubkey(),
+            destination_token: None, // fn will create the ATA
+            payer: &update_authority,
+            authorization_rules: None,
+            args,
+        })
+        .await
+        .unwrap();
+
+        // Try to burn the wrong Token Record.
+        let args = BurnArgs::V1 { amount: 1 };
+
+        let mut builder = BurnBuilder::new();
+        builder
+            .authority(owner.pubkey())
+            .metadata(da.metadata)
+            .edition(da.edition.unwrap())
+            .mint(da.mint.pubkey())
+            .token(da.token.unwrap())
+            .token_record(da_other.token_record.unwrap());
+
+        let burn_ix = builder.build(args).unwrap().instruction();
+
+        let transaction = Transaction::new_signed_with_payer(
+            &[burn_ix],
+            Some(&context.payer.pubkey()),
+            &[&context.payer, &owner],
+            context.last_blockhash,
+        );
+
+        let err = context
+            .banks_client
+            .process_transaction(transaction)
+            .await
+            .unwrap_err();
+
+        assert_custom_error!(err, MetadataError::InvalidTokenRecord);
+    }
 }
 
 mod nft {
```
