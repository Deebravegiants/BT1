# [?] Merge pull request from GHSA-h8x4-pj5m-m4c6

## Summary
Severity: Unknown
Chain: Solana
Component: metaplex-foundation/mpl-token-metadata
Published: 2023-02-16
Source: https://github.com/metaplex-foundation/mpl-token-metadata/commit/efe9a1c27e0f485569828b5678ad384f41a7de53
Type: security-commit

## Details
Merge pull request from GHSA-h8x4-pj5m-m4c6

* WIP Transfer Out changes.

* Adding more intense account validation.

* Removing dumb copy paste errors.

* Adding warning.

* Adding edition derivation checks.

* do not decrement max supply

* Adding back lost check.

---------

Co-authored-by: blockiosaurus <blockiosaurus@gmail.com>

## Patch
### token-metadata/program/src/error.rs
```diff
@@ -687,6 +687,12 @@ pub enum MetadataError {
     /// 173
     #[error("Cannot update the rule set of a programmable asset that has a delegate")]
     CannotUpdateAssetWithDelegate,
+    #[error("Invalid Associated Token Account Program")]
+    InvalidAssociatedTokenAccountProgram,
+
+    /// 174
+    #[error("Invalid InstructionsSysvar")]
+    InvalidInstructionsSysvar,
 }
 
 impl PrintProgramError for MetadataError {
```

### token-metadata/program/src/processor/burn/burn_edition_nft.rs
```diff
@@ -232,23 +232,13 @@ pub fn process_burn_edition_nft(program_id: &Pubkey, accounts: &[AccountInfo]) -
     }
 
     // Decrement the suppply on the master edition now that we've successfully burned a print.
-    // Decrement max_supply if Master Edition owner is not the same as Print Edition owner.
     let mut master_edition: MasterEditionV2 =
         MasterEditionV2::from_account_info(master_edition_info)?;
     master_edition.supply = master_edition
         .supply
         .checked_sub(1)
         .ok_or(MetadataError::NumericalOverflowError)?;
 
-    if let Some(max_supply) = master_edition.max_supply {
-        if !owner_is_the_same {
-            master_edition.max_supply = Some(
-                max_supply
-                    .checked_sub(1)
-                    .ok_or(MetadataError::NumericalOverflowError)?,
-            );
-        }
-    }
     master_edition.serialize(&mut *master_edition_info.try_borrow_mut_data()?)?;
 
     Ok(())
```

### token-metadata/program/src/processor/escrow/close_escrow_account.rs
```diff
@@ -7,38 +7,44 @@ use solana_program::{
 };
 
 use crate::{
-    assertions::{assert_derivation, assert_initialized, assert_owned_by},
+    assertions::{assert_derivation, assert_initialized, assert_keys_equal, assert_owned_by},
     error::MetadataError,
-    state::{
-        EscrowAuthority, Metadata, TokenMetadataAccount, TokenOwnedEscrow, TokenStandard,
-        ESCROW_POSTFIX, PREFIX,
-    },
+    pda::{EDITION, PREFIX},
+    state::{EscrowAuthority, Metadata, TokenMetadataAccount, TokenOwnedEscrow, TokenStandard},
     utils::check_token_standard,
 };
 
+use super::find_escrow_seeds;
+
 pub fn process_close_escrow_account(
-    program_id: &Pubkey,
+    _program_id: &Pubkey,
     accounts: &[AccountInfo],
 ) -> ProgramResult {
     let account_info_iter = &mut accounts.iter();
 
     let escrow_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(escrow_account_info, &crate::ID)?;
+
     let metadata_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(metadata_account_info, &crate::ID)?;
+
     let mint_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(mint_account_info, &spl_token::id())?;
+
     let token_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(token_account_info, &spl_token::id())?;
+
     let edition_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(edition_account_info, &crate::ID)?;
+
     let payer_account_info = next_account_info(account_info_iter)?;
-    let system_account_info = next_account_info(account_info_iter)?;
+    assert_signer(payer_account_info)?;
 
+    let system_account_info = next_account_info(account_info_iter)?;
     if *system_account_info.key != system_program::id() {
         return Err(MetadataError::InvalidSystemProgram.into());
     }
 
-    assert_owned_by(metadata_account_info, program_id)?;
-    assert_owned_by(mint_account_info, &spl_token::id())?;
-    assert_owned_by(token_account_info, &spl_token::id())?;
-    assert_signer(payer_account_info)?;
-
     let metadata: Metadata = Metadata::from_account_info(metadata_account_info)?;
 
     // Mint account passed in must be the mint of the metadata account passed in.
@@ -52,20 +58,46 @@ pub fn process_close_escrow_account(
         return Err(MetadataError::MustBeNonFungible.into());
     };
 
-    let bump_seed = assert_derivation(
-        program_id,
-        escrow_account_info,
+    // Check that the edition account is for this mint.
+    let _edition_bump = assert_derivation(
+        &crate::ID,
+        edition_account_info,
         &[
             PREFIX.as_bytes(),
-            program_id.as_ref(),
+            crate::id().as_ref(),
             mint_account_info.key.as_ref(),
-            ESCROW_POSTFIX.as_bytes(),
+            EDITION.as_bytes(),
         ],
     )?;
 
-    assert_owned_by(escrow_account_info, program_id)?;
+    let token_account: spl_token::state::Account = assert_initialized(token_account_info)?;
+
+    if token_account.mint != *mint_account_info.key {
+        return Err(MetadataError::MintMismatch.into());
+    }
+
+    if token_account.amount != 1 {
+        return Err(MetadataError::NotEnoughTokens.into());
+    }
+
+    if token_account.mint != metadata.mint {
+        return Err(MetadataError::MintMismatch.into());
+    }
+
+    let creator_type = if token_account.owner == *payer_account_info.key {
+        EscrowAuthority::TokenOwner
+    } else {
+        EscrowAuthority::Creator(*payer_account_info.key)
+    };
+
+    // Derive the seeds for PDA signing.
+    let escrow_seeds = find_escrow_seeds(mint_account_info.key, &creator_type);
+
+    let bump_seed = assert_derivation(&crate::ID, escrow_account_info, &escrow_seeds)?;
+
     let token_account: spl_token::state::Account = assert_initialized(token_account_info)?;
     let toe = TokenOwnedEscrow::from_account_info(escrow_account_info)?;
+    assert_keys_equal(&toe.base_token, mint_account_info.key)?;
 
     if bump_seed != toe.bump {
         return Err(MetadataError::InvalidEscrowBumpSeed.into());
```

### token-metadata/program/src/processor/escrow/create_escrow_account.rs
```diff
@@ -5,32 +5,55 @@ use solana_program::{
     entrypoint::ProgramResult,
     program_memory::sol_memcpy,
     pubkey::Pubkey,
+    system_program,
 };
 
 use super::find_escrow_seeds;
 use crate::{
     assertions::{assert_derivation, assert_initialized, assert_owned_by},
     error::MetadataError,
+    pda::{EDITION, PREFIX},
     state::{
         EscrowAuthority, Key, Metadata, TokenMetadataAccount, TokenOwnedEscrow, TokenStandard,
     },
     utils::check_token_standard,
 };
 
 pub fn process_create_escrow_account(
-    program_id: &Pubkey,
+    _program_id: &Pubkey,
     accounts: &[AccountInfo],
 ) -> ProgramResult {
     let account_info_iter = &mut accounts.iter();
 
     let escrow_account_info = next_account_info(account_info_iter)?;
+    if escrow_account_info.owner != &system_program::ID || !escrow_account_info.data_is_empty() {
+        return Err(MetadataError::AlreadyInitialized.into());
+    }
+
     let metadata_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(metadata_account_info, &crate::ID)?;
+
     let mint_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(mint_account_info, &spl_token::id())?;
+
     let token_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(token_account_info, &spl_token::id())?;
+
     let edition_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(edition_account_info, &crate::ID)?;
+
     let payer_account_info = next_account_info(account_info_iter)?;
+    assert_signer(payer_account_info)?;
+
     let system_account_info = next_account_info(account_info_iter)?;
-    let _sysvar_ix_account_info = next_account_info(account_info_iter)?;
+    if *system_account_info.key != system_program::id() {
+        return Err(MetadataError::InvalidSystemProgram.into());
+    }
+
+    let sysvar_ix_account_info = next_account_info(account_info_iter)?;
+    if sysvar_ix_account_info.key != &solana_program::sysvar::instructions::ID {
+        return Err(MetadataError::InvalidInstructionsSysvar.into());
+    }
 
     let is_using_authority = account_info_iter.len() == 1;
 
@@ -40,11 +63,6 @@ pub fn process_create_escrow_account(
         None
     };
 
-    assert_owned_by(metadata_account_info, program_id)?;
-    assert_owned_by(mint_account_info, &spl_token::id())?;
-    assert_owned_by(token_account_info, &spl_token::id())?;
-    assert_signer(payer_account_info)?;
-
     let metadata: Metadata = Metadata::from_account_info(metadata_account_info)?;
 
     // Mint account passed in must be the mint of the metadata account passed in.
@@ -59,7 +77,20 @@ pub fn process_create_escrow_account(
         return Err(MetadataError::MustBeNonFungible.into());
     };
 
+    // Check that the edition account is for this mint.
+    let _edition_bump = assert_derivation(
+        &crate::ID,
+        edition_account_info,
+        &[
+            PREFIX.as_bytes(),
+            crate::id().as_ref(),
+            mint_account_info.key.as_ref(),
+            EDITION.as_bytes(),
+        ],
+    )?;
+
     let creator = maybe_authority_info.unwrap_or(payer_account_info);
+    assert_signer(creator)?;
 
     let token_account: spl_token::state::Account = assert_initialized(token_account_info)?;
 
@@ -85,7 +116,7 @@ pub fn process_create_escrow_account(
     let escrow_seeds = find_escrow_seeds(mint_account_info.key, &creator_type);
 
     let bump_seed = &[assert_derivation(
-        &crate::id(),
+        &crate::ID,
         escrow_account_info,
         &escrow_seeds,
     )?];
@@ -106,7 +137,7 @@ pub fn process_create_escrow_account(
 
     // Create the account.
     create_or_allocate_account_raw(
-        *program_id,
+        crate::ID,
         escrow_account_info,
         system_account_info,
         payer_account_info,
```

### token-metadata/program/src/processor/escrow/transfer_out.rs
```diff
@@ -17,24 +17,57 @@ use crate::{
 };
 
 pub fn process_transfer_out_of_escrow(
-    program_id: &Pubkey,
+    _program_id: &Pubkey,
     accounts: &[AccountInfo],
     args: TransferOutOfEscrowArgs,
 ) -> ProgramResult {
     let account_info_iter = &mut accounts.iter();
 
     let escrow_info = next_account_info(account_info_iter)?;
-    let _metadata_info = next_account_info(account_info_iter)?;
+    assert_owned_by(escrow_info, &crate::ID)?;
+
+    // Currently unused, if used in the future the mint of the metadata should
+    // be verified against the escrow mint.
+    let metadata_info = next_account_info(account_info_iter)?;
+    assert_owned_by(metadata_info, &crate::ID)?;
+
     let payer_info = next_account_info(account_info_iter)?;
+    assert_signer(payer_info)?;
+
     let attribute_mint_info = next_account_info(account_info_iter)?;
+    assert_owned_by(attribute_mint_info, &spl_token::ID)?;
+
     let attribute_src_info = next_account_info(account_info_iter)?;
+    assert_owned_by(attribute_src_info, &spl_token::ID)?;
+
+    // We don't check attribute destination ownership because it may not be initialized yet.
     let attribute_dst_info = next_account_info(account_info_iter)?;
+
     let escrow_mint_info = next_account_info(account_info_iter)?;
+    assert_owned_by(escrow_mint_info, &spl_token::ID)?;
+
     let escrow_account_info = next_account_info(account_info_iter)?;
-    let system_account_info = next_account_info(account_info_iter)?;
+    assert_owned_by(escrow_account_info, &spl_token::ID)?;
+
+    let system_program_info = next_account_info(account_info_iter)?;
+    if system_program_info.key != &solana_program::system_program::ID {
+        return Err(MetadataError::InvalidSystemProgram.into());
+    }
+
     let ata_program_info = next_account_info(account_info_iter)?;
+    if ata_program_info.key != &spl_associated_token_account::ID {
+        return Err(MetadataError::InvalidAssociatedTokenAccountProgram.into());
+    }
+
     let token_program_info = next_account_info(account_info_iter)?;
-    let _sysvar_ix_account_info = next_account_info(account_info_iter)?;
+    if token_program_info.key != &spl_token::ID {
+        return Err(MetadataError::InvalidTokenProgram.into());
+    }
+
+    let sysvar_ix_account_info = next_account_info(account_info_iter)?;
+    if sysvar_ix_account_info.key != &solana_program::sysvar::instructions::ID {
+        return Err(MetadataError::InvalidInstructionsSysvar.into());
+    }
 
     // Allow the option to set a different authority than the payer.
     let is_using_authority = account_info_iter.len() == 1;
@@ -47,7 +80,6 @@ pub fn process_transfer_out_of_escrow(
     };
     let authority = maybe_authority_info.unwrap_or(payer_info);
 
-    assert_owned_by(escrow_info, program_id)?;
     let toe = TokenOwnedEscrow::from_account_info(escrow_info)?;
 
     // Derive the seeds for PDA signing.
@@ -56,8 +88,6 @@ pub fn process_transfer_out_of_escrow(
     let bump_seed = &[assert_derivation(&crate::id(), escrow_info, &escrow_seeds)?];
     let escrow_authority_seeds = [escrow_seeds, vec![bump_seed]].concat();
 
-    assert_signer(payer_info)?;
-
     // Allocate the target ATA if it doesn't exist.
     if !is_initialized_account(&attribute_dst_info.data.borrow()) {
         #[allow(deprecated)]
@@ -75,7 +105,7 @@ pub fn process_transfer_out_of_escrow(
                 payer_info.clone(),
                 attribute_dst_info.clone(),
                 attribute_mint_info.clone(),
-                system_account_info.clone(),
+                system_program_info.clone(),
                 token_program_info.clone(),
                 ata_program_info.clone(),
             ],
@@ -96,6 +126,13 @@ pub fn process_transfer_out_of_escrow(
 
     // Check that the authority matches based on the authority type.
     let escrow_account = spl_token::state::Account::unpack(&escrow_account_info.data.borrow())?;
+    if escrow_account.mint != *escrow_mint_info.key {
+        return Err(MetadataError::MintMismatch.into());
+    }
+    if escrow_account.amount != 1 {
+        return Err(MetadataError::AmountMustBeGreaterThanZero.into());
+    }
+
     match toe.authority {
         EscrowAuthority::TokenOwner => {
             if escrow_account.owner != *authority.key {
```
