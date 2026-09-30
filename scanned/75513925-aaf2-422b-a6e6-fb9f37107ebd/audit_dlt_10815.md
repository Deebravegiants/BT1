# [?] Fix overflow when amounts are u64::MAX (#310)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-program/token
Published: 2020-08-25
Source: https://github.com/solana-program/token/commit/4badc18ec2e44c29a222bb7615b45109e1c663d0
Type: security-commit

## Details
Fix overflow when amounts are u64::MAX (#310)

## Patch
### program/src/error.rs
```diff
@@ -43,6 +43,9 @@ pub enum TokenError {
     /// Invalid instruction
     #[error("Invalid instruction")]
     InvalidInstruction,
+    /// Operation overflowed
+    #[error("Operation overflowed")]
+    Overflow,
 }
 impl From<TokenError> for ProgramError {
     fn from(e: TokenError) -> Self {
```

### program/src/processor.rs
```diff
@@ -170,7 +170,10 @@ impl Processor {
         };
 
         source_account.amount -= amount;
-        dest_account.amount += amount;
+        dest_account.amount = dest_account
+            .amount
+            .checked_add(amount)
+            .ok_or(TokenError::Overflow)?;
 
         if source_account.is_native {
             **source_account_info.lamports.borrow_mut() -= amount;
@@ -304,7 +307,10 @@ impl Processor {
             }
         }
 
-        dest_account.amount += amount;
+        dest_account.amount = dest_account
+            .amount
+            .checked_add(amount)
+            .ok_or(TokenError::Overflow)?;
 
         Ok(())
     }
@@ -497,6 +503,7 @@ impl PrintProgramError for TokenError {
                 info!("Error: Instruction does not support non-native tokens")
             }
             TokenError::InvalidInstruction => info!("Error: Invalid instruction"),
+            TokenError::Overflow => info!("Error: Operation overflowed"),
         }
     }
 }
@@ -2190,4 +2197,153 @@ mod tests {
         assert_eq!(account.amount, 0);
         assert_eq!(account3_account.lamports, 4);
     }
+
+    #[test]
+    fn test_overflow() {
+        let program_id = pubkey_rand();
+        let account_key = pubkey_rand();
+        let mut account_account = SolanaAccount::new(0, size_of::<Account>(), &program_id);
+        let account2_key = pubkey_rand();
+        let mut account2_account = SolanaAccount::new(0, size_of::<Account>(), &program_id);
+        let owner_key = pubkey_rand();
+        let mut owner_account = SolanaAccount::default();
+        let owner2_key = pubkey_rand();
+        let mut owner2_account = SolanaAccount::default();
+        let mint_owner_key = pubkey_rand();
+        let mut mint_owner_account = SolanaAccount::default();
+        let mint_key = pubkey_rand();
+        let mut mint_account = SolanaAccount::new(0, size_of::<Mint>(), &program_id);
+
+        // create victim account
+        do_process_instruction(
+            initialize_account(&program_id, &account_key, &mint_key, &owner_key).unwrap(),
+            vec![&mut account_account, &mut mint_account, &mut owner_account],
+        )
+        .unwrap();
+
+        // create another account
+        do_process_instruction(
+            initialize_account(&program_id, &account2_key, &mint_key, &owner2_key).unwrap(),
+            vec![
+                &mut account2_account,
+                &mut mint_account,
+                &mut owner2_account,
+            ],
+        )
+        .unwrap();
+
+        // create new mint with owner
+        do_process_instruction(
+            initialize_mint(&program_id, &mint_key, None, Some(&mint_owner_key), 0, 2).unwrap(),
+            vec![&mut mint_account, &mut mint_owner_account],
+        )
+        .unwrap();
+
+        // mint the max to attacker
+        do_process_instruction(
+            mint_to(
+                &program_id,
+                &mint_key,
+                &account2_key,
+                &mint_owner_key,
+                &[],
+                42,
+            )
+            .unwrap(),
+            vec![
+                &mut mint_account,
+                &mut account2_account,
+                &mut mint_owner_account,
+            ],
+        )
+        .unwrap();
+        let account: &mut Account = state::unpack(&mut account2_account.data).unwrap();
+        assert_eq!(account.amount, 42);
+
+        // mint the max to victum
+        do_process_instruction(
+            mint_to(
+                &program_id,
+                &mint_key,
+                &account_key,
+                &mint_owner_key,
+                &[],
+                u64::MAX,
+            )
+            .unwrap(),
+            vec![
+                &mut mint_account,
+                &mut account_account,
+                &mut mint_owner_account,
+            ],
+        )
+        .unwrap();
+        let account: &mut Account = state::unpack(&mut account_account.data).unwrap();
+        assert_eq!(account.amount, u64::MAX);
+
+        // mint one more
+        assert_eq!(
+            Err(TokenError::Overflow.into()),
+            do_process_instruction(
+                mint_to(
+                    &program_id,
+                    &mint_key,
+                    &account_key,
+                    &mint_owner_key,
+                    &[],
+                    1,
+                )
+                .unwrap(),
+                vec![
+                    &mut mint_account,
+                    &mut account_account,
+                    &mut mint_owner_account,
+                ],
+            )
+        );
+
+        // mint back to large amount
+        let account: &mut Account = state::unpack(&mut account_account.data).unwrap();
+        account.amount = 0;
+        do_process_instruction(
+            mint_to(
+                &program_id,
+                &mint_key,
+                &account_key,
+                &mint_owner_key,
+                &[],
+                u64::MAX,
+            )
+            .unwrap(),
+            vec![
+                &mut mint_account,
+                &mut account_account,
+                &mut mint_owner_account,
+            ],
+        )
+        .unwrap();
+        let account: &mut Account = state::unpack(&mut account_account.data).unwrap();
+        assert_eq!(account.amount, u64::MAX);
+
+        // transfer to burn victim
+        assert_eq!(
+            Err(TokenError::Overflow.into()),
+            do_process_instruction(
+                transfer(
+                    &program_id,
+                    &account2_key,
+                    &account_key,
+                    &owner2_key,
+                    &[],
+                    1,
+                )
+                .unwrap(),
+                vec![
+                    &mut account2_account,
+                    &mut account_account,
+                    &mut owner2_account,
+                ],
+            )
+        );
+    }
 }
```
