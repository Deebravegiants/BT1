# [?] Merge pull request #24 from Squads-Protocol/refactor/reentrancy-prevention

## Summary
Severity: Unknown
Chain: Solana
Component: Squads-Protocol/v4
Published: 2023-08-28
Source: https://github.com/Squads-Protocol/v4/commit/df514e1e6c5753992278ca82bdd524c32c45d612
Type: security-commit

## Details
Merge pull request #24 from Squads-Protocol/refactor/reentrancy-prevention

enforce ms accounts readonly in CPI instead of reentrancy checks

## Patch
### programs/multisig/src/errors.rs
```diff
@@ -32,8 +32,6 @@ pub enum MultisigError {
     InvalidNumberOfAccounts,
     #[msg("Invalid account provided")]
     InvalidAccount,
-    #[msg("`transaction_execute` reentrancy is forbidden")]
-    ExecuteReentrancy,
     #[msg("Cannot remove last member")]
     RemoveLastMember,
     #[msg("Members don't include any voters")]
@@ -62,4 +60,6 @@ pub enum MultisigError {
     DecimalsMismatch,
     #[msg("Member has unknown permission")]
     UnknownPermission,
+    #[msg("Account is protected, it cannot be passed into a CPI as writable")]
+    ProtectedAccount,
 }
```

### programs/multisig/src/instructions/batch_execute_transaction.rs
```diff
@@ -104,7 +104,7 @@ impl BatchExecuteTransaction<'_> {
 
     /// Execute a transaction from the batch.
     #[access_control(ctx.accounts.validate())]
-    pub fn batch_execute_transaction(ctx: Context<BatchExecuteTransaction>) -> Result<()> {
+    pub fn batch_execute_transaction(ctx: Context<Self>) -> Result<()> {
         let multisig = &mut ctx.accounts.multisig;
         let proposal = &mut ctx.accounts.proposal;
         let batch = &mut ctx.accounts.batch;
@@ -146,11 +146,7 @@ impl BatchExecuteTransaction<'_> {
             &ephemeral_signer_keys,
         )?;
 
-        let current_status = proposal.status.clone();
-        // Set the proposal state to Executing to prevent reentrancy attacks (e.g. cancelling proposal) in the middle of execution.
-        proposal.status = ProposalStatus::Executing;
-        let proposal_account_info = proposal.to_account_info();
-        proposal.try_serialize(&mut &mut proposal_account_info.data.borrow_mut()[..])?;
+        let protected_accounts = &[proposal.key(), batch_key];
 
         // Execute the transaction message instructions one-by-one.
         executable_message.execute_message(
@@ -159,11 +155,9 @@ impl BatchExecuteTransaction<'_> {
                 .map(|seed| seed.to_vec())
                 .collect::<Vec<Vec<u8>>>(),
             &ephemeral_signer_seeds,
+            protected_accounts,
         )?;
 
-        // Restore the proposal status after execution.
-        proposal.status = current_status;
-
         // Increment the executed transaction index.
         batch.executed_transaction_index = batch
             .executed_transaction_index
```

### programs/multisig/src/instructions/vault_transaction_execute.rs
```diff
@@ -28,7 +28,6 @@ pub struct VaultTransactionExecute<'info> {
 
     /// The transaction to execute.
     #[account(
-        mut,
         seeds = [
             SEED_PREFIX,
             multisig.key().as_ref(),
@@ -39,7 +38,6 @@ pub struct VaultTransactionExecute<'info> {
     )]
     pub transaction: Account<'info, VaultTransaction>,
 
-    #[account(mut)]
     pub member: Signer<'info>,
     // `remaining_accounts` must include the following accounts in the exact order:
     // 1. AddressLookupTable accounts in the order they appear in `message.address_table_lookups`.
@@ -128,10 +126,7 @@ impl VaultTransactionExecute<'_> {
             &ephemeral_signer_keys,
         )?;
 
-        // Set the proposal state to Executing to prevent reentrancy attacks (e.g. cancelling proposal) in the middle of execution.
-        proposal.status = ProposalStatus::Executing;
-        let proposal_account_info = proposal.to_account_info();
-        proposal.try_serialize(&mut &mut proposal_account_info.data.borrow_mut()[..])?;
+        let protected_accounts = &[proposal.key()];
 
         // Execute the transaction message instructions one-by-one.
         executable_message.execute_message(
@@ -140,6 +135,7 @@ impl VaultTransactionExecute<'_> {
                 .map(|seed| seed.to_vec())
                 .collect::<Vec<Vec<u8>>>(),
             &ephemeral_signer_seeds,
+            protected_accounts,
         )?;
 
         // Mark the proposal as executed.
```

### programs/multisig/src/state/proposal.rs
```diff
@@ -137,6 +137,9 @@ pub enum ProposalStatus {
     /// Proposal has been approved and is pending execution.
     Approved { timestamp: i64 },
     /// Proposal is being executed. This is a transient state that always transitions to `Executed` in the span of a single transaction.
+    #[deprecated(
+        note = "This status used to be used to prevent reentrancy attacks. It is no longer needed."
+    )]
     Executing,
     /// Proposal has been executed.
     Executed { timestamp: i64 },
```

### programs/multisig/src/utils/executable_transaction_message.rs
```diff
@@ -4,11 +4,9 @@ use std::convert::From;
 use anchor_lang::prelude::*;
 use anchor_lang::solana_program::instruction::Instruction;
 use anchor_lang::solana_program::program::invoke_signed;
-use anchor_lang::Discriminator;
 use solana_address_lookup_table_program::state::AddressLookupTable;
 
 use crate::errors::*;
-use crate::id;
 use crate::state::*;
 
 /// Sanitized and validated combination of a `MsTransactionMessage` and `AccountInfo`s it references.
@@ -171,21 +169,23 @@ impl<'a, 'info> ExecutableTransactionMessage<'a, 'info> {
         })
     }
 
+    /// Executes all instructions in the message via CPI calls.
+    /// # Arguments
+    /// * `vault_seeds` - Seeds for the vault PDA.
+    /// * `ephemeral_signer_seeds` - Seeds for the ephemeral signer PDAs.
+    /// * `protected_accounts` - Accounts that must not be passed as writable to the CPI calls to prevent potential reentrancy attacks.
     pub fn execute_message(
         &self,
         vault_seeds: &[Vec<u8>],
         ephemeral_signer_seeds: &[Vec<Vec<u8>>],
+        protected_accounts: &[Pubkey],
     ) -> Result<()> {
         for (ix, account_infos) in self.to_instructions_and_accounts().iter() {
-            // Make sure we don't allow reentrancy of transaction_execute.
-            if ix.program_id == id() {
-                require!(
-                    ix.data[..8] != crate::instruction::VaultTransactionExecute::DISCRIMINATOR,
-                    MultisigError::ExecuteReentrancy
-                );
+            // Make sure we don't pass protected accounts as writable to CPI calls.
+            for account_meta in ix.accounts.iter().filter(|m| m.is_writable) {
                 require!(
-                    ix.data[..8] != crate::instruction::BatchExecuteTransaction::DISCRIMINATOR,
-                    MultisigError::ExecuteReentrancy
+                    !protected_accounts.contains(&account_meta.pubkey),
+                    MultisigError::ProtectedAccount
                 );
             }
 
```

### sdk/multisig/idl/multisig.json
```diff
@@ -396,15 +396,15 @@
         },
         {
           "name": "transaction",
-          "isMut": true,
+          "isMut": false,
           "isSigner": false,
           "docs": [
             "The transaction to execute."
           ]
         },
         {
           "name": "member",
-          "isMut": true,
+          "isMut": false,
           "isSigner": true
         }
       ],
@@ -2113,78 +2113,78 @@
     },
     {
       "code": 6015,
-      "name": "ExecuteReentrancy",
-      "msg": "`transaction_execute` reentrancy is forbidden"
-    },
-    {
-      "code": 6016,
       "name": "RemoveLastMember",
       "msg": "Cannot remove last member"
     },
     {
-      "code": 6017,
+      "code": 6016,
       "name": "NoVoters",
       "msg": "Members don't include any voters"
     },
     {
-      "code": 6018,
+      "code": 6017,
       "name": "NoProposers",
       "msg": "Members don't include any proposers"
     },
     {
-      "code": 6019,
+      "code": 6018,
       "name": "NoExecutors",
       "msg": "Members don't include any executors"
     },
     {
-      "code": 6020,
+      "code": 6019,
       "name": "InvalidStaleTransactionIndex",
       "msg": "`stale_transaction_index` must be <= `transaction_index`"
     },
     {
-      "code": 6021,
+      "code": 6020,
       "name": "NotSupportedForControlled",
       "msg": "Instruction not supported for controlled multisig"
     },
     {
-      "code": 6022,
+      "code": 6021,
       "name": "TimeLockNotReleased",
       "msg": "Proposal time lock has not been released"
     },
     {
-      "code": 6023,
+      "code": 6022,
       "name": "NoActions",
       "msg": "Config transaction must have at least one action"
     },
     {
-      "code": 6024,
+      "code": 6023,
       "name": "MissingAccount",
       "msg": "Missing account"
     },
     {
-      "code": 6025,
+      "code": 6024,
       "name": "InvalidMint",
       "msg": "Invalid mint"
     },
     {
-      "code": 6026,
+      "code": 6025,
       "name": "InvalidDestination",
       "msg": "Invalid destination"
     },
     {
-      "code": 6027,
+      "code": 6026,
       "name": "SpendingLimitExceeded",
       "msg": "Spending limit exceeded"
     },
     {
-      "code": 6028,
+      "code": 6027,
       "name": "DecimalsMismatch",
       "msg": "Decimals don't match the mint"
     },
     {
-      "code": 6029,
+      "code": 6028,
       "name": "UnknownPermission",
       "msg": "Member has unknown permission"
+    },
+    {
+      "code": 6029,
+      "name": "ProtectedAccount",
+      "msg": "Account is protected, it cannot be passed into a CPI as writable"
     }
   ],
   "metadata": {
```

### sdk/multisig/src/generated/errors/index.ts
```diff
@@ -343,37 +343,14 @@ export class InvalidAccountError extends Error {
 createErrorFromCodeLookup.set(0x177e, () => new InvalidAccountError())
 createErrorFromNameLookup.set('InvalidAccount', () => new InvalidAccountError())
 
-/**
- * ExecuteReentrancy: '`transaction_execute` reentrancy is forbidden'
- *
- * @category Errors
- * @category generated
- */
-export class ExecuteReentrancyError extends Error {
-  readonly code: number = 0x177f
-  readonly name: string = 'ExecuteReentrancy'
-  constructor() {
-    super('`transaction_execute` reentrancy is forbidden')
-    if (typeof Error.captureStackTrace === 'function') {
-      Error.captureStackTrace(this, ExecuteReentrancyError)
-    }
-  }
-}
-
-createErrorFromCodeLookup.set(0x177f, () => new ExecuteReentrancyError())
-createErrorFromNameLookup.set(
-  'ExecuteReentrancy',
-  () => new ExecuteReentrancyError()
-)
-
 /**
  * RemoveLastMember: 'Cannot remove last member'
  *
  * @category Errors
  * @category generated
  */
 export class RemoveLastMemberError extends Error {
-  readonly code: number = 0x1780
+  readonly code: number = 0x177f
   readonly name: string = 'RemoveLastMember'
   constructor() {
     super('Cannot remove last member')
@@ -383,7 +360,7 @@ export class RemoveLastMemberError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x1780, () => new RemoveLastMemberError())
+createErrorFromCodeLookup.set(0x177f, () => new RemoveLastMemberError())
 createErrorFromNameLookup.set(
   'RemoveLastMember',
   () => new RemoveLastMemberError()
@@ -396,7 +373,7 @@ createErrorFromNameLookup.set(
  * @category generated
  */
 export class NoVotersError extends Error {
-  readonly code: number = 0x1781
+  readonly code: number = 0x1780
   readonly name: string = 'NoVoters'
   constructor() {
     super("Members don't include any voters")
@@ -406,7 +383,7 @@ export class NoVotersError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x1781, () => new NoVotersError())
+createErrorFromCodeLookup.set(0x1780, () => new NoVotersError())
 createErrorFromNameLookup.set('NoVoters', () => new NoVotersError())
 
 /**
@@ -416,7 +393,7 @@ createErrorFromNameLookup.set('NoVoters', () => new NoVotersError())
  * @category generated
  */
 export class NoProposersError extends Error {
-  readonly code: number = 0x1782
+  readonly code: number = 0x1781
   readonly name: string = 'NoProposers'
   constructor() {
     super("Members don't include any proposers")
@@ -426,7 +403,7 @@ export class NoProposersError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x1782, () => new NoProposersError())
+createErrorFromCodeLookup.set(0x1781, () => new NoProposersError())
 createErrorFromNameLookup.set('NoProposers', () => new NoProposersError())
 
 /**
@@ -436,7 +413,7 @@ createErrorFromNameLookup.set('NoProposers', () => new NoProposersError())
  * @category generated
  */
 export class NoExecutorsError extends Error {
-  readonly code: number = 0x1783
+  readonly code: number = 0x1782
   readonly name: string = 'NoExecutors'
   constructor() {
     super("Members don't include any executors")
@@ -446,7 +423,7 @@ export class NoExecutorsError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x1783, () => new NoExecutorsError())
+createErrorFromCodeLookup.set(0x1782, () => new NoExecutorsError())
 createErrorFromNameLookup.set('NoExecutors', () => new NoExecutorsError())
 
 /**
@@ -456,7 +433,7 @@ createErrorFromNameLookup.set('NoExecutors', () => new NoExecutorsError())
  * @category generated
  */
 export class InvalidStaleTransactionIndexError extends Error {
-  readonly code: number = 0x1784
+  readonly code: number = 0x1783
   readonly name: string = 'InvalidStaleTransactionIndex'
   constructor() {
     super('`stale_transaction_index` must be <= `transaction_index`')
@@ -467,7 +444,7 @@ export class InvalidStaleTransactionIndexError extends Error {
 }
 
 createErrorFromCodeLookup.set(
-  0x1784,
+  0x1783,
   () => new InvalidStaleTransactionIndexError()
 )
 createErrorFromNameLookup.set(
@@ -482,7 +459,7 @@ createErrorFromNameLookup.set(
  * @category generated
  */
 export class NotSupportedForControlledError extends Error {
-  readonly code: number = 0x1785
+  readonly code: number = 0x1784
   readonly name: string = 'NotSupportedForControlled'
   constructor() {
     super('Instruction not supported for controlled multisig')
@@ -493,7 +470,7 @@ export class NotSupportedForControlledError extends Error {
 }
 
 createErrorFromCodeLookup.set(
-  0x1785,
+  0x1784,
   () => new NotSupportedForControlledError()
 )
 createErrorFromNameLookup.set(
@@ -508,7 +485,7 @@ createErrorFromNameLookup.set(
  * @category generated
  */
 export class TimeLockNotReleasedError extends Error {
-  readonly code: number = 0x1786
+  readonly code: number = 0x1785
   readonly name: string = 'TimeLockNotReleased'
   constructor() {
     super('Proposal time lock has not been released')
@@ -518,7 +495,7 @@ export class TimeLockNotReleasedError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x1786, () => new TimeLockNotReleasedError())
+createErrorFromCodeLookup.set(0x1785, () => new TimeLockNotReleasedError())
 createErrorFromNameLookup.set(
   'TimeLockNotReleased',
   () => new TimeLockNotReleasedError()
@@ -531,7 +508,7 @@ createErrorFromNameLookup.set(
  * @category generated
  */
 export class NoActionsError extends Error {
-  readonly code: number = 0x1787
+  readonly code: number = 0x1786
   readonly name: string = 'NoActions'
   constructor() {
     super('Config transaction must have at least one action')
@@ -541,7 +518,7 @@ export class NoActionsError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x1787, () => new NoActionsError())
+createErrorFromCodeLookup.set(0x1786, () => new NoActionsError())
 createErrorFromNameLookup.set('NoActions', () => new NoActionsError())
 
 /**
@@ -551,7 +528,7 @@ createErrorFromNameLookup.set('NoActions', () => new NoActionsError())
  * @category generated
  */
 export class MissingAccountError extends Error {
-  readonly code: number = 0x1788
+  readonly code: number = 0x1787
   readonly name: string = 'MissingAccount'
   constructor() {
     super('Missing account')
@@ -561,7 +538,7 @@ export class MissingAccountError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x1788, () => new MissingAccountError())
+createErrorFromCodeLookup.set(0x1787, () => new MissingAccountError())
 createErrorFromNameLookup.set('MissingAccount', () => new MissingAccountError())
 
 /**
@@ -571,7 +548,7 @@ createErrorFromNameLookup.set('MissingAccount', () => new MissingAccountError())
  * @category generated
  */
 export class InvalidMintError extends Error {
-  readonly code: number = 0x1789
+  readonly code: number = 0x1788
   readonly name: string = 'InvalidMint'
   constructor() {
     super('Invalid mint')
@@ -581,7 +558,7 @@ export class InvalidMintError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x1789, () => new InvalidMintError())
+createErrorFromCodeLookup.set(0x1788, () => new InvalidMintError())
 createErrorFromNameLookup.set('InvalidMint', () => new InvalidMintError())
 
 /**
@@ -591,7 +568,7 @@ createErrorFromNameLookup.set('InvalidMint', () => new InvalidMintError())
  * @category generated
  */
 export class InvalidDestinationError extends Error {
-  readonly code: number = 0x178a
+  readonly code: number = 0x1789
   readonly name: string = 'InvalidDestination'
   constructor() {
     super('Invalid destination')
@@ -601,7 +578,7 @@ export class InvalidDestinationError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x178a, () => new InvalidDestinationError())
+createErrorFromCodeLookup.set(0x1789, () => new InvalidDestinationError())
 createErrorFromNameLookup.set(
   'InvalidDestination',
   () => new InvalidDestinationError()
@@ -614,7 +591,7 @@ createErrorFromNameLookup.set(
  * @category generated
  */
 export class SpendingLimitExceededError extends Error {
-  readonly code: number = 0x178b
+  readonly code: number = 0x178a
   readonly name: string = 'SpendingLimitExceeded'
   constructor() {
     super('Spending limit exceeded')
@@ -624,7 +601,7 @@ export class SpendingLimitExceededError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x178b, () => new SpendingLimitExceededError())
+createErrorFromCodeLookup.set(0x178a, () => new SpendingLimitExceededError())
 createErrorFromNameLookup.set(
   'SpendingLimitExceeded',
   () => new SpendingLimitExceededError()
@@ -637,7 +614,7 @@ createErrorFromNameLookup.set(
  * @category generated
  */
 export class DecimalsMismatchError extends Error {
-  readonly code: number = 0x178c
+  readonly code: number = 0x178b
   readonly name: string = 'DecimalsMismatch'
   constructor() {
     super("Decimals don't match the mint")
@@ -647,7 +624,7 @@ export class DecimalsMismatchError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x178c, () => new DecimalsMismatchError())
+createErrorFromCodeLookup.set(0x178b, () => new DecimalsMismatchError())
 createErrorFromNameLookup.set(
   'DecimalsMismatch',
   () => new DecimalsMismatchError()
@@ -660,7 +637,7 @@ createErrorFromNameLookup.set(
  * @category generated
  */
 export class UnknownPermissionError extends Error {
-  readonly code: number = 0x178d
+  readonly code: number = 0x178c
   readonly name: string = 'UnknownPermission'
   constructor() {
     super('Member has unknown permission')
@@ -670,12 +647,35 @@ export class UnknownPermissionError extends Error {
   }
 }
 
-createErrorFromCodeLookup.set(0x178d, () => new UnknownPermissionError())
+createErrorFromCodeLookup.set(0x178c, () => new UnknownPermissionError())
 createErrorFromNameLookup.set(
   'UnknownPermission',
   () => new UnknownPermissionError()
 )
 
+/**
+ * ProtectedAccount: 'Account is protected, it cannot be passed into a CPI as writable'
+ *
+ * @category Errors
+ * @category generated
+ */
+export class ProtectedAccountError extends Error {
+  readonly code: number = 0x178d
+  readonly name: string = 'ProtectedAccount'
+  constructor() {
+    super('Account is protected, it cannot be passed into a CPI as writable')
+    if (typeof Error.captureStackTrace === 'function') {
+      Error.captureStackTrace(this, ProtectedAccountError)
+    }
+  }
+}
+
+createErrorFromCodeLookup.set(0x178d, () => new ProtectedAccountError())
+createErrorFromNameLookup.set(
+  'ProtectedAccount',
+  () => new ProtectedAccountError()
+)
+
 /**
  * Attempts to resolve a custom program error from the provided error code.
  * @category Errors
```

### sdk/multisig/src/generated/instructions/vaultTransactionExecute.ts
```diff
@@ -24,8 +24,8 @@ export const vaultTransactionExecuteStruct = new beet.BeetArgsStruct<{
  *
  * @property [] multisig
  * @property [_writable_] proposal
- * @property [_writable_] transaction
- * @property [_writable_, **signer**] member
+ * @property [] transaction
+ * @property [**signer**] member
  * @category Instructions
  * @category VaultTransactionExecute
  * @category generated
@@ -70,12 +70,12 @@ export function createVaultTransactionExecuteInstruction(
     },
     {
       pubkey: accounts.transaction,
-      isWritable: true,
+      isWritable: false,
       isSigner: false,
     },
     {
       pubkey: accounts.member,
-      isWritable: true,
+      isWritable: false,
       isSigner: true,
     },
   ]
```
