# [?] Fix potential vulnerabilities in programs using spl-token CPIs by adding program id checks (#1714)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2021-05-12
Source: https://github.com/solana-labs/solana-program-library/commit/58221fc9ae05e258ee903b49c5e8f5abbeb7796c
Type: security-commit

## Details
Fix potential vulnerabilities in programs using spl-token CPIs by adding program id checks (#1714)

* Add spl-token program id check helper function. Add program id to instruction bindings.

* Run cargo fmt

* Fixup tests

* Skip ATA tests when custom token program-id

Co-authored-by: Tyera Eulberg <tyera@solana.com>

## Patch
### token-swap/program/src/processor.rs
```diff
@@ -1197,8 +1197,6 @@ mod tests {
 
     // Test program id for the swap program.
     const SWAP_PROGRAM_ID: Pubkey = Pubkey::new_from_array([2u8; 32]);
-    // Test program id for the token program.
-    const TOKEN_PROGRAM_ID: Pubkey = Pubkey::new_from_array([1u8; 32]);
 
     struct TestSyscallStubs {}
     impl program_stubs::SyscallStubs for TestSyscallStubs {
@@ -1213,7 +1211,7 @@ mod tests {
             let mut new_account_infos = vec![];
 
             // mimic check for token program in accounts
-            if !account_infos.iter().any(|x| *x.key == TOKEN_PROGRAM_ID) {
+            if !account_infos.iter().any(|x| *x.key == spl_token::id()) {
                 return Err(ProgramError::InvalidAccountData);
             }
 
@@ -1287,37 +1285,37 @@ mod tests {
                 Pubkey::find_program_address(&[&swap_key.to_bytes()[..]], &SWAP_PROGRAM_ID);
 
             let (pool_mint_key, mut pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &authority_key, None);
+                create_mint(&spl_token::id(), &authority_key, None);
             let (pool_token_key, pool_token_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &pool_mint_key,
                 &mut pool_mint_account,
                 &authority_key,
                 &user_key,
                 0,
             );
             let (pool_fee_key, pool_fee_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &pool_mint_key,
                 &mut pool_mint_account,
                 &authority_key,
                 &user_key,
                 0,
             );
             let (token_a_mint_key, mut token_a_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &user_key, None);
+                create_mint(&spl_token::id(), &user_key, None);
             let (token_a_key, token_a_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &token_a_mint_key,
                 &mut token_a_mint_account,
                 &user_key,
                 &authority_key,
                 token_a_amount,
             );
             let (token_b_mint_key, mut token_b_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &user_key, None);
+                create_mint(&spl_token::id(), &user_key, None);
             let (token_b_key, token_b_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &token_b_mint_key,
                 &mut token_b_mint_account,
                 &user_key,
@@ -1353,7 +1351,7 @@ mod tests {
             do_process_instruction(
                 initialize(
                     &SWAP_PROGRAM_ID,
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &self.swap_key,
                     &self.authority_key,
                     &self.token_a_key,
@@ -1388,23 +1386,23 @@ mod tests {
             pool_amount: u64,
         ) -> (Pubkey, Account, Pubkey, Account, Pubkey, Account) {
             let (token_a_key, token_a_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &self.token_a_mint_key,
                 &mut self.token_a_mint_account,
                 &mint_owner,
                 &account_owner,
                 a_amount,
             );
             let (token_b_key, token_b_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &self.token_b_mint_key,
                 &mut self.token_b_mint_account,
                 &mint_owner,
                 &account_owner,
                 b_amount,
             );
             let (pool_key, pool_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &self.pool_mint_key,
                 &mut self.pool_mint_account,
                 &self.authority_key,
@@ -1458,7 +1456,7 @@ mod tests {
             // approve moving from user source account
             do_process_instruction(
                 approve(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &user_source_key,
                     &user_transfer_key,
                     &user_key,
@@ -1481,7 +1479,7 @@ mod tests {
             do_process_instruction(
                 swap(
                     &SWAP_PROGRAM_ID,
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &self.swap_key,
                     &self.authority_key,
                     &user_transfer_key,
@@ -1535,7 +1533,7 @@ mod tests {
             let user_transfer_authority = Pubkey::new_unique();
             do_process_instruction(
                 approve(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &depositor_token_a_key,
                     &user_transfer_authority,
                     &depositor_key,
@@ -1553,7 +1551,7 @@ mod tests {
 
             do_process_instruction(
                 approve(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &depositor_token_b_key,
                     &user_transfer_authority,
                     &depositor_key,
@@ -1572,7 +1570,7 @@ mod tests {
             do_process_instruction(
                 deposit_all_token_types(
                     &SWAP_PROGRAM_ID,
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &self.swap_key,
                     &self.authority_key,
                     &user_transfer_authority,
@@ -1622,7 +1620,7 @@ mod tests {
             // approve user transfer authority to take out pool tokens
             do_process_instruction(
                 approve(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &pool_key,
                     &user_transfer_authority_key,
                     &user_key,
@@ -1642,7 +1640,7 @@ mod tests {
             do_process_instruction(
                 withdraw_all_token_types(
                     &SWAP_PROGRAM_ID,
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &self.swap_key,
                     &self.authority_key,
                     &user_transfer_authority_key,
@@ -1690,7 +1688,7 @@ mod tests {
             let user_transfer_authority_key = Pubkey::new_unique();
             do_process_instruction(
                 approve(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &deposit_account_key,
                     &user_transfer_authority_key,
                     &depositor_key,
@@ -1709,7 +1707,7 @@ mod tests {
             do_process_instruction(
                 deposit_single_token_type_exact_amount_in(
                     &SWAP_PROGRAM_ID,
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &self.swap_key,
                     &self.authority_key,
                     &user_transfer_authority_key,
@@ -1753,7 +1751,7 @@ mod tests {
             // approve user transfer authority to take out pool tokens
             do_process_instruction(
                 approve(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &pool_key,
                     &user_transfer_authority_key,
                     &user_key,
@@ -1772,7 +1770,7 @@ mod tests {
             do_process_instruction(
                 withdraw_single_token_type_exact_amount_out(
                     &SWAP_PROGRAM_ID,
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &self.swap_key,
                     &self.authority_key,
                     &user_transfer_authority_key,
@@ -1951,7 +1949,7 @@ mod tests {
         let swap_key = Pubkey::new_unique();
         let mut mint = (Pubkey::new_unique(), Account::default());
         let mut destination = (Pubkey::new_unique(), Account::default());
-        let token_program = (TOKEN_PROGRAM_ID, Account::default());
+        let token_program = (spl_token::id(), Account::default());
         let (authority_key, nonce) =
             Pubkey::find_program_address(&[&swap_key.to_bytes()[..]], &SWAP_PROGRAM_ID);
         let mut authority = (authority_key, Account::default());
@@ -2023,7 +2021,7 @@ mod tests {
         // uninitialized token a account
         {
             let old_account = accounts.token_a_account;
-            accounts.token_a_account = Account::new(0, 0, &TOKEN_PROGRAM_ID);
+            accounts.token_a_account = Account::new(0, 0, &spl_token::id());
             assert_eq!(
                 Err(SwapError::ExpectedAccount.into()),
                 accounts.initialize_swap()
@@ -2034,7 +2032,7 @@ mod tests {
         // uninitialized token b account
         {
             let old_account = accounts.token_b_account;
-            accounts.token_b_account = Account::new(0, 0, &TOKEN_PROGRAM_ID);
+            accounts.token_b_account = Account::new(0, 0, &spl_token::id());
             assert_eq!(
                 Err(SwapError::ExpectedAccount.into()),
                 accounts.initialize_swap()
@@ -2045,7 +2043,7 @@ mod tests {
         // uninitialized pool mint
         {
             let old_account = accounts.pool_mint_account;
-            accounts.pool_mint_account = Account::new(0, 0, &TOKEN_PROGRAM_ID);
+            accounts.pool_mint_account = Account::new(0, 0, &spl_token::id());
             assert_eq!(
                 Err(SwapError::ExpectedMint.into()),
                 accounts.initialize_swap()
@@ -2056,7 +2054,7 @@ mod tests {
         // token A account owner is not swap authority
         {
             let (_token_a_key, token_a_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.token_a_mint_key,
                 &mut accounts.token_a_mint_account,
                 &user_key,
@@ -2075,7 +2073,7 @@ mod tests {
         // token B account owner is not swap authority
         {
             let (_token_b_key, token_b_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.token_b_mint_key,
                 &mut accounts.token_b_mint_account,
                 &user_key,
@@ -2094,7 +2092,7 @@ mod tests {
         // pool token account owner is swap authority
         {
             let (_pool_token_key, pool_token_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.pool_mint_key,
                 &mut accounts.pool_mint_account,
                 &accounts.authority_key,
@@ -2113,7 +2111,7 @@ mod tests {
         // pool fee account owner is swap authority
         {
             let (_pool_fee_key, pool_fee_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.pool_mint_key,
                 &mut accounts.pool_mint_account,
                 &accounts.authority_key,
@@ -2132,7 +2130,7 @@ mod tests {
         // pool mint authority is not swap authority
         {
             let (_pool_mint_key, pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &user_key, None);
+                create_mint(&spl_token::id(), &user_key, None);
             let old_mint = accounts.pool_mint_account;
             accounts.pool_mint_account = pool_mint_account;
             assert_eq!(
@@ -2145,7 +2143,7 @@ mod tests {
         // pool mint token has freeze authority
         {
             let (_pool_mint_key, pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &accounts.authority_key, Some(&user_key));
+                create_mint(&spl_token::id(), &accounts.authority_key, Some(&user_key));
             let old_mint = accounts.pool_mint_account;
             accounts.pool_mint_account = pool_mint_account;
             assert_eq!(
@@ -2158,7 +2156,7 @@ mod tests {
         // token A account owned by wrong program
         {
             let (_token_a_key, mut token_a_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.token_a_mint_key,
                 &mut accounts.token_a_mint_account,
                 &user_key,
@@ -2178,7 +2176,7 @@ mod tests {
         // token B account owned by wrong program
         {
             let (_token_b_key, mut token_b_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.token_b_mint_key,
                 &mut accounts.token_b_mint_account,
                 &user_key,
@@ -2198,7 +2196,7 @@ mod tests {
         // empty token A account
         {
             let (_token_a_key, token_a_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.token_a_mint_key,
                 &mut accounts.token_a_mint_account,
                 &user_key,
@@ -2217,7 +2215,7 @@ mod tests {
         // empty token B account
         {
             let (_token_b_key, token_b_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.token_b_mint_key,
                 &mut accounts.token_b_mint_account,
                 &user_key,
@@ -2239,11 +2237,11 @@ mod tests {
             let old_pool_account = accounts.pool_token_account;
 
             let (_pool_mint_key, pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &accounts.authority_key, None);
+                create_mint(&spl_token::id(), &accounts.authority_key, None);
             accounts.pool_mint_account = pool_mint_account;
 
             let (_empty_pool_token_key, empty_pool_token_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.pool_mint_key,
                 &mut accounts.pool_mint_account,
                 &accounts.authority_key,
@@ -2252,7 +2250,7 @@ mod tests {
             );
 
             let (_pool_token_key, pool_token_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.pool_mint_key,
                 &mut accounts.pool_mint_account,
                 &accounts.authority_key,
@@ -2281,7 +2279,7 @@ mod tests {
         // pool fee account has wrong mint
         {
             let (_pool_fee_key, pool_fee_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.token_a_mint_key,
                 &mut accounts.token_a_mint_account,
                 &user_key,
@@ -2301,7 +2299,7 @@ mod tests {
         {
             do_process_instruction(
                 approve(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.token_a_key,
                     &user_key,
                     &accounts.authority_key,
@@ -2323,7 +2321,7 @@ mod tests {
 
             do_process_instruction(
                 revoke(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.token_a_key,
                     &accounts.authority_key,
                     &[],
@@ -2338,7 +2336,7 @@ mod tests {
         {
             do_process_instruction(
                 approve(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.token_b_key,
                     &user_key,
                     &accounts.authority_key,
@@ -2360,7 +2358,7 @@ mod tests {
 
             do_process_instruction(
                 revoke(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.token_b_key,
                     &accounts.authority_key,
                     &[],
@@ -2375,7 +2373,7 @@ mod tests {
         {
             do_process_instruction(
                 set_authority(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.token_a_key,
                     Some(&user_key),
                     AuthorityType::CloseAccount,
@@ -2393,7 +2391,7 @@ mod tests {
 
             do_process_instruction(
                 set_authority(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.token_a_key,
                     None,
                     AuthorityType::CloseAccount,
@@ -2410,7 +2408,7 @@ mod tests {
         {
             do_process_instruction(
                 set_authority(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.token_b_key,
                     Some(&user_key),
                     AuthorityType::CloseAccount,
@@ -2428,7 +2426,7 @@ mod tests {
 
             do_process_instruction(
                 set_authority(
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.token_b_key,
                     None,
                     AuthorityType::CloseAccount,
@@ -2479,7 +2477,7 @@ mod tests {
         // create swap with same token A and B
         {
             let (_token_a_repeat_key, token_a_repeat_account) = mint_token(
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.token_a_mint_key,
                 &mut accounts.token_a_mint_account,
                 &user_key,
@@ -2635,7 +2633,7 @@ mod tests {
                 do_process_instruction_with_fee_constraints(
                     initialize(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &accounts.token_a_key,
@@ -2707,7 +2705,7 @@ mod tests {
                 do_process_instruction_with_fee_constraints(
                     initialize(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &accounts.token_a_key,
@@ -2775,7 +2773,7 @@ mod tests {
             do_process_instruction_with_fee_constraints(
                 initialize(
                     &SWAP_PROGRAM_ID,
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.swap_key,
                     &accounts.authority_key,
                     &accounts.token_a_key,
@@ -2915,7 +2913,7 @@ mod tests {
             ) = accounts.setup_token_accounts(&user_key, &depositor_key, deposit_a, deposit_b, 0);
             let old_swap_account = accounts.swap_account;
             let mut wrong_swap_account = old_swap_account.clone();
-            wrong_swap_account.owner = TOKEN_PROGRAM_ID;
+            wrong_swap_account.owner = spl_token::id();
             accounts.swap_account = wrong_swap_account;
             assert_eq!(
                 Err(ProgramError::IncorrectProgramId),
@@ -2948,7 +2946,7 @@ mod tests {
             let old_authority = accounts.authority_key;
             let (bad_authority_key, _nonce) = Pubkey::find_program_address(
                 &[&accounts.swap_key.to_bytes()[..]],
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
             );
             accounts.authority_key = bad_authority_key;
             assert_eq!(
@@ -3113,7 +3111,7 @@ mod tests {
                 do_process_instruction(
                     deposit_all_token_types(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &user_transfer_authority_key,
@@ -3270,7 +3268,7 @@ mod tests {
                 mut pool_account,
             ) = accounts.setup_token_accounts(&user_key, &depositor_key, deposit_a, deposit_b, 0);
             let (pool_mint_key, pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &accounts.authority_key, None);
+                create_mint(&spl_token::id(), &accounts.authority_key, None);
             let old_pool_key = accounts.pool_mint_key;
             let old_pool_account = accounts.pool_mint_account;
             accounts.pool_mint_key = pool_mint_key;
@@ -3529,7 +3527,7 @@ mod tests {
             ) = accounts.setup_token_accounts(&user_key, &withdrawer_key, initial_a, initial_b, 0);
             let old_swap_account = accounts.swap_account;
             let mut wrong_swap_account = old_swap_account.clone();
-            wrong_swap_account.owner = TOKEN_PROGRAM_ID;
+            wrong_swap_account.owner = spl_token::id();
             accounts.swap_account = wrong_swap_account;
             assert_eq!(
                 Err(ProgramError::IncorrectProgramId),
@@ -3562,7 +3560,7 @@ mod tests {
             let old_authority = accounts.authority_key;
             let (bad_authority_key, _nonce) = Pubkey::find_program_address(
                 &[&accounts.swap_key.to_bytes()[..]],
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
             );
             accounts.authority_key = bad_authority_key;
             assert_eq!(
@@ -3771,7 +3769,7 @@ mod tests {
                 do_process_instruction(
                     withdraw_all_token_types(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &user_transfer_authority_key,
@@ -3950,7 +3948,7 @@ mod tests {
                 initial_pool.try_into().unwrap(),
             );
             let (pool_mint_key, pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &accounts.authority_key, None);
+                create_mint(&spl_token::id(), &accounts.authority_key, None);
             let old_pool_key = accounts.pool_mint_key;
             let old_pool_account = accounts.pool_mint_account;
             accounts.pool_mint_key = pool_mint_key;
@@ -4330,7 +4328,7 @@ mod tests {
             ) = accounts.setup_token_accounts(&user_key, &depositor_key, deposit_a, deposit_b, 0);
             let old_swap_account = accounts.swap_account;
             let mut wrong_swap_account = old_swap_account.clone();
-            wrong_swap_account.owner = TOKEN_PROGRAM_ID;
+            wrong_swap_account.owner = spl_token::id();
             accounts.swap_account = wrong_swap_account;
             assert_eq!(
                 Err(ProgramError::IncorrectProgramId),
@@ -4360,7 +4358,7 @@ mod tests {
             let old_authority = accounts.authority_key;
             let (bad_authority_key, _nonce) = Pubkey::find_program_address(
                 &[&accounts.swap_key.to_bytes()[..]],
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
             );
             accounts.authority_key = bad_authority_key;
             assert_eq!(
@@ -4460,7 +4458,7 @@ mod tests {
                 do_process_instruction(
                     deposit_single_token_type_exact_amount_in(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &user_transfer_authority_key,
@@ -4605,7 +4603,7 @@ mod tests {
                 mut pool_account,
             ) = accounts.setup_token_accounts(&user_key, &depositor_key, deposit_a, deposit_b, 0);
             let (pool_mint_key, pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &accounts.authority_key, None);
+                create_mint(&spl_token::id(), &accounts.authority_key, None);
             let old_pool_key = accounts.pool_mint_key;
             let old_pool_account = accounts.pool_mint_account;
             accounts.pool_mint_key = pool_mint_key;
@@ -4846,7 +4844,7 @@ mod tests {
             ) = accounts.setup_token_accounts(&user_key, &withdrawer_key, initial_a, initial_b, 0);
             let old_swap_account = accounts.swap_account;
             let mut wrong_swap_account = old_swap_account.clone();
-            wrong_swap_account.owner = TOKEN_PROGRAM_ID;
+            wrong_swap_account.owner = spl_token::id();
             accounts.swap_account = wrong_swap_account;
             assert_eq!(
                 Err(ProgramError::IncorrectProgramId),
@@ -4876,7 +4874,7 @@ mod tests {
             let old_authority = accounts.authority_key;
             let (bad_authority_key, _nonce) = Pubkey::find_program_address(
                 &[&accounts.swap_key.to_bytes()[..]],
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
             );
             accounts.authority_key = bad_authority_key;
             assert_eq!(
@@ -5026,7 +5024,7 @@ mod tests {
                 do_process_instruction(
                     withdraw_single_token_type_exact_amount_out(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &user_transfer_authority_key,
@@ -5193,7 +5191,7 @@ mod tests {
                 initial_pool.try_into().unwrap(),
             );
             let (pool_mint_key, pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &accounts.authority_key, None);
+                create_mint(&spl_token::id(), &accounts.authority_key, None);
             let old_pool_key = accounts.pool_mint_key;
             let old_pool_account = accounts.pool_mint_account;
             accounts.pool_mint_key = pool_mint_key;
@@ -5750,7 +5748,7 @@ mod tests {
         do_process_instruction_with_fee_constraints(
             initialize(
                 &SWAP_PROGRAM_ID,
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.swap_key,
                 &accounts.authority_key,
                 &accounts.token_a_key,
@@ -5801,7 +5799,7 @@ mod tests {
         do_process_instruction_with_fee_constraints(
             swap(
                 &SWAP_PROGRAM_ID,
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
                 &accounts.swap_key,
                 &accounts.authority_key,
                 &accounts.authority_key,
@@ -5927,7 +5925,7 @@ mod tests {
             ) = accounts.setup_token_accounts(&user_key, &swapper_key, initial_a, initial_b, 0);
             let old_swap_account = accounts.swap_account;
             let mut wrong_swap_account = old_swap_account.clone();
-            wrong_swap_account.owner = TOKEN_PROGRAM_ID;
+            wrong_swap_account.owner = spl_token::id();
             accounts.swap_account = wrong_swap_account;
             assert_eq!(
                 Err(ProgramError::IncorrectProgramId),
@@ -5959,7 +5957,7 @@ mod tests {
             let old_authority = accounts.authority_key;
             let (bad_authority_key, _nonce) = Pubkey::find_program_address(
                 &[&accounts.swap_key.to_bytes()[..]],
-                &TOKEN_PROGRAM_ID,
+                &spl_token::id(),
             );
             accounts.authority_key = bad_authority_key;
             assert_eq!(
@@ -6070,7 +6068,7 @@ mod tests {
                 do_process_instruction(
                     swap(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &user_transfer_key,
@@ -6166,7 +6164,7 @@ mod tests {
                 _pool_account,
             ) = accounts.setup_token_accounts(&user_key, &swapper_key, initial_a, initial_b, 0);
             let (pool_mint_key, pool_mint_account) =
-                create_mint(&TOKEN_PROGRAM_ID, &accounts.authority_key, None);
+                create_mint(&spl_token::id(), &accounts.authority_key, None);
             let old_pool_key = accounts.pool_mint_key;
             let old_pool_account = accounts.pool_mint_account;
             accounts.pool_mint_key = pool_mint_key;
@@ -6239,7 +6237,7 @@ mod tests {
                 do_process_instruction(
                     swap(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &user_transfer_key,
@@ -6397,7 +6395,7 @@ mod tests {
             do_process_instruction_with_fee_constraints(
                 swap(
                     &SWAP_PROGRAM_ID,
-                    &TOKEN_PROGRAM_ID,
+                    &spl_token::id(),
                     &accounts.swap_key,
                     &accounts.authority_key,
                     &accounts.authority_key,
@@ -6471,7 +6469,7 @@ mod tests {
                 do_process_instruction_with_fee_constraints(
                     swap(
                         &SWAP_PROGRAM_ID,
-                        &TOKEN_PROGRAM_ID,
+                        &spl_token::id(),
                         &accounts.swap_key,
                         &accounts.authority_key,
                         &accounts.authority_key,
```

### token/js/cli/main.js
```diff
@@ -26,14 +26,17 @@ import {
 } from './token-test';
 
 async function main() {
+  const programVersion = process.env.PROGRAM_VERSION;
   console.log('Run test: loadTokenProgram');
   await loadTokenProgram();
   console.log('Run test: createMint');
   await createMint();
   console.log('Run test: createAccount');
   await createAccount();
-  console.log('Run test: createAssociatedAccount');
-  await createAssociatedAccount();
+  if (programVersion) {
+    console.log('Run test: createAssociatedAccount');
+    await createAssociatedAccount();
+  }
   console.log('Run test: mintTo');
   await mintTo();
   console.log('Run test: mintToChecked');
@@ -42,8 +45,10 @@ async function main() {
   await transfer();
   console.log('Run test: transferChecked');
   await transferChecked();
-  console.log('Run test: transferCheckedAssociated');
-  await transferCheckedAssociated();
+  if (programVersion) {
+    console.log('Run test: transferCheckedAssociated');
+    await transferCheckedAssociated();
+  }
   console.log('Run test: approveRevoke');
   await approveRevoke();
   console.log('Run test: failOnApproveOverspend');
```

### token/program/src/instruction.rs
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

### token/program/src/lib.rs
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

### token/program/src/processor.rs
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
