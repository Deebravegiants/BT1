# [?] fix(execution): prevent reentrancy attacks with cancelling proposal during execution

## Summary
Severity: Unknown
Chain: Solana
Component: Squads-Protocol/v4
Published: 2023-06-23
Source: https://github.com/Squads-Protocol/v4/commit/8416203ccb3128ea996baaf6500b908d212be50c
Type: security-commit

## Details
fix(execution): prevent reentrancy attacks with cancelling proposal during execution

## Patch
### programs/multisig/src/instructions/batch_execute_transaction.rs
```diff
@@ -1,4 +1,5 @@
 use anchor_lang::prelude::*;
+use std::borrow::Borrow;
 
 use crate::errors::*;
 use crate::state::*;
@@ -146,6 +147,10 @@ impl BatchExecuteTransaction<'_> {
             &ephemeral_signer_keys,
         )?;
 
+        let current_status = proposal.status.clone();
+        // Set the proposal state to Executing to prevent reentrancy attacks (e.g. cancelling proposal) in the middle of execution.
+        proposal.status = ProposalStatus::Executing;
+
         // Execute the transaction message instructions one-by-one.
         executable_message.execute_message(
             &vault_seeds
@@ -155,6 +160,9 @@ impl BatchExecuteTransaction<'_> {
             &ephemeral_signer_seeds,
         )?;
 
+        // Restore the proposal status after execution.
+        proposal.status = current_status;
+
         // Increment the executed transaction index.
         batch.executed_transaction_index = batch
             .executed_transaction_index
```

### programs/multisig/src/instructions/vault_transaction_execute.rs
```diff
@@ -128,6 +128,9 @@ impl VaultTransactionExecute<'_> {
             &ephemeral_signer_keys,
         )?;
 
+        // Set the proposal state to Executing to prevent reentrancy attacks (e.g. cancelling proposal) in the middle of execution.
+        proposal.status = ProposalStatus::Executing;
+
         // Execute the transaction message instructions one-by-one.
         executable_message.execute_message(
             &vault_seeds
```

### programs/multisig/src/state/proposal.rs
```diff
@@ -136,6 +136,8 @@ pub enum ProposalStatus {
     Rejected { timestamp: i64 },
     /// Proposal has been approved and is pending execution.
     Approved { timestamp: i64 },
+    /// Proposal is being executed. This is a transient state that always transitions to `Executed` in the span of a single transaction.
+    Executing,
     /// Proposal has been executed.
     Executed { timestamp: i64 },
     /// Proposal has been cancelled.
```

### sdk/multisig/idl/multisig.json
```diff
@@ -1988,6 +1988,9 @@
               }
             ]
           },
+          {
+            "name": "Executing"
+          },
           {
             "name": "Executed",
             "fields": [
```

### sdk/multisig/src/generated/types/ProposalStatus.ts
```diff
@@ -20,6 +20,7 @@ export type ProposalStatusRecord = {
   Active: { timestamp: beet.bignum }
   Rejected: { timestamp: beet.bignum }
   Approved: { timestamp: beet.bignum }
+  Executing: void /* scalar variant */
   Executed: { timestamp: beet.bignum }
   Cancelled: { timestamp: beet.bignum }
 }
@@ -49,6 +50,9 @@ export const isProposalStatusRejected = (
 export const isProposalStatusApproved = (
   x: ProposalStatus
 ): x is ProposalStatus & { __kind: 'Approved' } => x.__kind === 'Approved'
+export const isProposalStatusExecuting = (
+  x: ProposalStatus
+): x is ProposalStatus & { __kind: 'Executing' } => x.__kind === 'Executing'
 export const isProposalStatusExecuted = (
   x: ProposalStatus
 ): x is ProposalStatus & { __kind: 'Executed' } => x.__kind === 'Executed'
@@ -92,6 +96,7 @@ export const proposalStatusBeet = beet.dataEnum<ProposalStatusRecord>([
       'ProposalStatusRecord["Approved"]'
     ),
   ],
+  ['Executing', beet.unit],
 
   [
     'Executed',
```
