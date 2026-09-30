# [?] Fix potential vulnerabilities in programs using spl-token CPIs by adding program id checks (#1714)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-program/token
Published: 2021-05-12
Source: https://github.com/solana-program/token/commit/38751ab1fd22c8cf6e9e14575905242753cf591a
Type: security-commit

## Details
Fix potential vulnerabilities in programs using spl-token CPIs by adding program id checks (#1714)

* Add spl-token program id check helper function. Add program id to instruction bindings.

* Run cargo fmt

* Fixup tests

* Skip ATA tests when custom token program-id

Co-authored-by: Tyera Eulberg <tyera@solana.com>

## Patch
### program/src/instruction.rs
```diff
@@ -1,6 +1,6 @@
 //! Instruction types
 
-use crate::error::TokenError;
+use crate::{check_program_account, error::TokenError};
 use solana_program::{
     instruction::{AccountMeta, Instruction},
     program_error::ProgramError,
@@ -620,6 +620,7 @@ pub fn initialize_mint(
     freeze_authority_pubkey: Option<&Pubkey>,
     decimals: u8,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let freeze_authority = freeze_authority_pubkey.cloned().into();
     let data = TokenInstruction::InitializeMint {
         mint_authority: *mint_authority_pubkey,
@@ -647,6 +648,7 @@ pub fn initialize_account(
     mint_pubkey: &Pubkey,
     owner_pubkey: &Pubkey,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::InitializeAccount.pack();
 
     let accounts = vec![
@@ -670,6 +672,7 @@ pub fn initialize_account2(
     mint_pubkey: &Pubkey,
     owner_pubkey: &Pubkey,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::InitializeAccount2 {
         owner: *owner_pubkey,
     }
@@ -695,6 +698,7 @@ pub fn initialize_multisig(
     signer_pubkeys: &[&Pubkey],
     m: u8,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     if !is_valid_signer_index(m as usize)
         || !is_valid_signer_index(signer_pubkeys.len())
         || m as usize > signer_pubkeys.len()
@@ -726,6 +730,7 @@ pub fn transfer(
     signer_pubkeys: &[&Pubkey],
     amount: u64,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::Transfer { amount }.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
@@ -755,6 +760,7 @@ pub fn approve(
     signer_pubkeys: &[&Pubkey],
     amount: u64,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::Approve { amount }.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
@@ -782,6 +788,7 @@ pub fn revoke(
     owner_pubkey: &Pubkey,
     signer_pubkeys: &[&Pubkey],
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::Revoke.pack();
 
     let mut accounts = Vec::with_capacity(2 + signer_pubkeys.len());
@@ -810,6 +817,7 @@ pub fn set_authority(
     owner_pubkey: &Pubkey,
     signer_pubkeys: &[&Pubkey],
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let new_authority = new_authority_pubkey.cloned().into();
     let data = TokenInstruction::SetAuthority {
         authority_type,
@@ -843,6 +851,7 @@ pub fn mint_to(
     signer_pubkeys: &[&Pubkey],
     amount: u64,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::MintTo { amount }.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
@@ -872,6 +881,7 @@ pub fn burn(
     signer_pubkeys: &[&Pubkey],
     amount: u64,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::Burn { amount }.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
@@ -900,6 +910,7 @@ pub fn close_account(
     owner_pubkey: &Pubkey,
     signer_pubkeys: &[&Pubkey],
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::CloseAccount.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
@@ -928,6 +939,7 @@ pub fn freeze_account(
     owner_pubkey: &Pubkey,
     signer_pubkeys: &[&Pubkey],
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::FreezeAccount.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
@@ -956,6 +968,7 @@ pub fn thaw_account(
     owner_pubkey: &Pubkey,
     signer_pubkeys: &[&Pubkey],
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::ThawAccount.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
@@ -988,6 +1001,7 @@ pub fn transfer_checked(
     amount: u64,
     decimals: u8,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::TransferChecked { amount, decimals }.pack();
 
     let mut accounts = Vec::with_capacity(4 + signer_pubkeys.len());
@@ -1021,6 +1035,7 @@ pub fn approve_checked(
     amount: u64,
     decimals: u8,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::ApproveChecked { amount, decimals }.pack();
 
     let mut accounts = Vec::with_capacity(4 + signer_pubkeys.len());
@@ -1052,6 +1067,7 @@ pub fn mint_to_checked(
     amount: u64,
     decimals: u8,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::MintToChecked { amount, decimals }.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
@@ -1082,6 +1098,7 @@ pub fn burn_checked(
     amount: u64,
     decimals: u8,
 ) -> Result<Instruction, ProgramError> {
+    check_program_account(token_program_id)?;
     let data = TokenInstruction::BurnChecked { amount, decimals }.pack();
 
     let mut accounts = Vec::with_capacity(3 + signer_pubkeys.len());
```

### program/src/lib.rs
```diff
@@ -14,6 +14,7 @@ mod entrypoint;
 
 // Export current sdk types for downstream users building with a different sdk version
 pub use solana_program;
+use solana_program::{entrypoint::ProgramResult, program_error::ProgramError, pubkey::Pubkey};
 
 /// Convert the UI representation of a token amount (using the decimals field defined in its mint)
 /// to the raw amount
@@ -27,3 +28,11 @@ pub fn amount_to_ui_amount(amount: u64, decimals: u8) -> f64 {
 }
 
 solana_program::declare_id!("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA");
+
+/// Checks that the supplied program ID is the correct one for SPL-token
+pub fn check_program_account(spl_token_program_id: &Pubkey) -> ProgramResult {
+    if spl_token_program_id != &id() {
+        return Err(ProgramError::IncorrectProgramId);
+    }
+    Ok(())
+}
```

### program/src/processor.rs
```diff
@@ -985,7 +985,7 @@ mod tests {
 
     #[test]
     fn test_initialize_mint() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let owner_key = Pubkey::new_unique();
         let mint_key = Pubkey::new_unique();
         let mut mint_account = SolanaAccount::new(42, Mint::get_packed_len(), &program_id);
@@ -1033,7 +1033,7 @@ mod tests {
 
     #[test]
     fn test_initialize_mint_account() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(42, Account::get_packed_len(), &program_id);
         let owner_key = Pubkey::new_unique();
@@ -1109,7 +1109,7 @@ mod tests {
 
     #[test]
     fn test_transfer_dups() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account1_key = Pubkey::new_unique();
         let mut account1_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -1416,7 +1416,7 @@ mod tests {
 
     #[test]
     fn test_transfer() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -1837,7 +1837,7 @@ mod tests {
 
     #[test]
     fn test_self_transfer() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -2367,7 +2367,7 @@ mod tests {
 
     #[test]
     fn test_mintable_token_with_zero_supply() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -2466,7 +2466,7 @@ mod tests {
 
     #[test]
     fn test_approve_dups() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account1_key = Pubkey::new_unique();
         let mut account1_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -2677,7 +2677,7 @@ mod tests {
 
     #[test]
     fn test_approve() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -2882,7 +2882,7 @@ mod tests {
 
     #[test]
     fn test_set_authority_dups() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account1_key = Pubkey::new_unique();
         let mut account1_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -2985,7 +2985,7 @@ mod tests {
 
     #[test]
     fn test_set_authority() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -3324,7 +3324,7 @@ mod tests {
 
     #[test]
     fn test_mint_to_dups() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account1_key = Pubkey::new_unique();
         let mut account1_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -3420,7 +3420,7 @@ mod tests {
 
     #[test]
     fn test_mint_to() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -3623,7 +3623,7 @@ mod tests {
 
     #[test]
     fn test_burn_dups() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account1_key = Pubkey::new_unique();
         let mut account1_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -3823,7 +3823,7 @@ mod tests {
 
     #[test]
     fn test_burn() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -4088,7 +4088,7 @@ mod tests {
 
     #[test]
     fn test_multisig() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let mint_key = Pubkey::new_unique();
         let mut mint_account =
             SolanaAccount::new(mint_minimum_balance(), Mint::get_packed_len(), &program_id);
@@ -4492,7 +4492,7 @@ mod tests {
 
     #[test]
     fn test_validate_owner() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let owner_key = Pubkey::new_unique();
         let mut signer_keys = [Pubkey::default(); MAX_SIGNERS];
         for signer_key in signer_keys.iter_mut().take(MAX_SIGNERS) {
@@ -4652,7 +4652,7 @@ mod tests {
 
     #[test]
     fn test_close_account_dups() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account1_key = Pubkey::new_unique();
         let mut account1_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -4738,7 +4738,7 @@ mod tests {
 
     #[test]
     fn test_close_account() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let mint_key = Pubkey::new_unique();
         let mut mint_account =
             SolanaAccount::new(mint_minimum_balance(), Mint::get_packed_len(), &program_id);
@@ -4967,7 +4967,7 @@ mod tests {
 
     #[test]
     fn test_native_token() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let mut mint_account =
             SolanaAccount::new(mint_minimum_balance(), Mint::get_packed_len(), &program_id);
         let account_key = Pubkey::new_unique();
@@ -5144,7 +5144,7 @@ mod tests {
 
     #[test]
     fn test_overflow() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -5321,7 +5321,7 @@ mod tests {
 
     #[test]
     fn test_frozen() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -5507,7 +5507,7 @@ mod tests {
 
     #[test]
     fn test_freeze_thaw_dups() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account1_key = Pubkey::new_unique();
         let mut account1_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -5571,7 +5571,7 @@ mod tests {
 
     #[test]
     fn test_freeze_account() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
@@ -5684,7 +5684,7 @@ mod tests {
 
     #[test]
     fn test_initialize_account2() {
-        let program_id = Pubkey::new_unique();
+        let program_id = crate::id();
         let account_key = Pubkey::new_unique();
         let mut account_account = SolanaAccount::new(
             account_minimum_balance(),
```
