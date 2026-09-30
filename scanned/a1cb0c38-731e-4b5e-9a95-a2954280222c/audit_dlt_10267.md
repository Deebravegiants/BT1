# [?] fix: Fix panic on duplicate transaction submit

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-11-01
Source: https://github.com/radixdlt/babylon-node/commit/c0e192016f9df7d23dba3ec6703ef5800f801558
Type: security-commit

## Details
fix: Fix panic on duplicate transaction submit

## Patch
### core-rust/core-api-server/src/core_api/handlers/lts/transaction_status.rs
```diff
@@ -209,11 +209,14 @@ fn map_rejected_payloads_due_to_known_commit(
                 // commit, and we may see a "not-yet-updated" entry - luckily, in such case, we can
                 // precisely tell the transaction's status ourselves:
                 .unwrap_or_else(|| {
-                    MempoolRejectionReason::AlreadyCommitted(AlreadyCommittedError {
-                        notarized_transaction_hash,
-                        committed_state_version,
-                        committed_notarized_transaction_hash: *committed_notarized_transaction_hash,
-                    })
+                    MempoolRejectionReason::TransactionIntentAlreadyCommitted(
+                        AlreadyCommittedError {
+                            notarized_transaction_hash,
+                            committed_state_version,
+                            committed_notarized_transaction_hash:
+                                *committed_notarized_transaction_hash,
+                        },
+                    )
                     .to_string()
                 });
             Ok(models::LtsTransactionPayloadDetails {
```

### core-rust/core-api-server/src/core_api/handlers/lts/transaction_submit.rs
```diff
@@ -40,11 +40,7 @@ pub(crate) async fn handle_lts_transaction_submit(
         )),
         Err(MempoolAddError::Duplicate(_)) => Ok(models::LtsTransactionSubmitResponse::new(true)),
         Err(MempoolAddError::Rejected(rejection)) => {
-            if rejection.is_rejected_because_intent_already_committed() {
-                let already_committed_error = rejection
-                    .reason
-                    .already_committed_error()
-                    .expect("Already committed rejections should have an already_committed_error");
+            if let Some(already_committed_error) = rejection.transaction_intent_already_committed_error() {
                 Err(detailed_error(
                     StatusCode::BAD_REQUEST,
                     "The transaction intent has already been committed",
```

### core-rust/core-api-server/src/core_api/handlers/transaction_status.rs
```diff
@@ -211,11 +211,14 @@ fn map_rejected_payloads_due_to_known_commit(
                 // commit, and we may see a "not-yet-updated" entry - luckily, in such case, we can
                 // precisely tell the transaction's status ourselves:
                 .unwrap_or_else(|| {
-                    MempoolRejectionReason::AlreadyCommitted(AlreadyCommittedError {
-                        notarized_transaction_hash,
-                        committed_state_version,
-                        committed_notarized_transaction_hash: *committed_notarized_transaction_hash,
-                    })
+                    MempoolRejectionReason::TransactionIntentAlreadyCommitted(
+                        AlreadyCommittedError {
+                            notarized_transaction_hash,
+                            committed_state_version,
+                            committed_notarized_transaction_hash:
+                                *committed_notarized_transaction_hash,
+                        },
+                    )
                     .to_string()
                 });
             Ok(models::TransactionPayloadDetails {
```

### core-rust/core-api-server/src/core_api/handlers/transaction_submit.rs
```diff
@@ -35,11 +35,7 @@ pub(crate) async fn handle_transaction_submit(
         )),
         Err(MempoolAddError::Duplicate(_)) => Ok(models::TransactionSubmitResponse::new(true)),
         Err(MempoolAddError::Rejected(rejection)) => {
-            if rejection.is_rejected_because_intent_already_committed() {
-                let already_committed_error = rejection
-                    .reason
-                    .already_committed_error()
-                    .expect("Already committed rejections should have an already_committed_error");
+            if let Some(already_committed_error) = rejection.transaction_intent_already_committed_error() {
                 Err(detailed_error(
                     StatusCode::BAD_REQUEST,
                     "The transaction intent has already been committed",
```

### core-rust/state-manager/src/mempool/metrics.rs
```diff
@@ -152,7 +152,7 @@ impl MetricLabel for MempoolAddResult {
             None => "Added",
             Some(MempoolAddError::PriorityThresholdNotMet { .. }) => "PriorityThresholdNotMet",
             Some(MempoolAddError::Rejected(rejection)) => match &rejection.reason {
-                MempoolRejectionReason::AlreadyCommitted(_) => "AlreadyCommitted",
+                MempoolRejectionReason::TransactionIntentAlreadyCommitted(_) => "AlreadyCommitted",
                 MempoolRejectionReason::FromExecution(_) => "ExecutionError",
                 MempoolRejectionReason::ValidationError(_) => "ValidationError",
             },
```

### core-rust/state-manager/src/mempool/mod.rs
```diff
@@ -134,15 +134,15 @@ impl MempoolAddRejection {
         }
     }
 
-    pub fn is_rejected_because_intent_already_committed(&self) -> bool {
+    pub fn transaction_intent_already_committed_error(&self) -> Option<&AlreadyCommittedError> {
         match &self.against_state {
             AtState::Specific(specific) => match specific {
                 AtSpecificState::Committed { .. } => {
-                    self.reason.is_rejected_because_intent_already_committed()
+                    self.reason.transaction_intent_already_committed_error()
                 }
-                AtSpecificState::PendingPreparingVertices { .. } => false,
+                AtSpecificState::PendingPreparingVertices { .. } => None,
             },
-            AtState::Static => false,
+            AtState::Static => None,
         }
     }
 }
```

### core-rust/state-manager/src/mempool/pending_transaction_result_cache.rs
```diff
@@ -13,7 +13,7 @@ pub type ExecutionRejectionReason = RejectionReason;
 
 #[derive(Debug, Clone, PartialEq, Eq)]
 pub enum MempoolRejectionReason {
-    AlreadyCommitted(AlreadyCommittedError),
+    TransactionIntentAlreadyCommitted(AlreadyCommittedError),
     FromExecution(Box<ExecutionRejectionReason>),
     ValidationError(TransactionValidationError),
 }
@@ -40,35 +40,19 @@ impl MempoolRejectionReason {
         self.permanence().is_permanent_for_intent()
     }
 
-    pub fn is_rejected_because_intent_already_committed(&self) -> bool {
+    pub fn transaction_intent_already_committed_error(&self) -> Option<&AlreadyCommittedError> {
         match self {
-            MempoolRejectionReason::AlreadyCommitted(_) => true,
-            MempoolRejectionReason::FromExecution(rejection_reason) => match **rejection_reason {
-                ExecutionRejectionReason::BootloadingError(_) => false,
-                ExecutionRejectionReason::SuccessButFeeLoanNotRepaid => false,
-                ExecutionRejectionReason::ErrorBeforeLoanAndDeferredCostsRepaid(_) => false,
-                ExecutionRejectionReason::TransactionEpochNotYetValid { .. } => false,
-                ExecutionRejectionReason::TransactionEpochNoLongerValid { .. } => false,
-                ExecutionRejectionReason::TransactionProposerTimestampNotYetValid { .. } => false,
-                ExecutionRejectionReason::TransactionProposerTimestampNoLongerValid { .. } => false,
-                ExecutionRejectionReason::IntentHashPreviouslyCommitted(_) => true,
-                ExecutionRejectionReason::IntentHashPreviouslyCancelled(_) => true,
-                ExecutionRejectionReason::SubintentsNotYetSupported => false,
-            },
-            MempoolRejectionReason::ValidationError(_) => false,
-        }
-    }
-
-    pub fn already_committed_error(&self) -> Option<&AlreadyCommittedError> {
-        match self {
-            MempoolRejectionReason::AlreadyCommitted(error) => Some(error),
-            _ => None,
+            MempoolRejectionReason::TransactionIntentAlreadyCommitted(already_committed_error) => {
+                Some(already_committed_error)
+            }
+            MempoolRejectionReason::FromExecution(_) => None,
+            MempoolRejectionReason::ValidationError(_) => None,
         }
     }
 
     pub fn permanence(&self) -> RejectionPermanence {
         match self {
-            MempoolRejectionReason::AlreadyCommitted(_) => {
+            MempoolRejectionReason::TransactionIntentAlreadyCommitted(_) => {
                 // This is permanent for the intent - because even other, non-committed transactions
                 // of the same intent will fail with `ExecutionRejectionReason::IntentHashPreviouslyCommitted`
                 RejectionPermanence::PermanentForAnyPayloadWithThisTransactionIntent
@@ -197,7 +181,7 @@ pub enum RetrySettings {
 impl fmt::Display for MempoolRejectionReason {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
         match self {
-            MempoolRejectionReason::AlreadyCommitted(error) => {
+            MempoolRejectionReason::TransactionIntentAlreadyCommitted(error) => {
                 write!(f, "Already committed: {error:?}")
             }
             MempoolRejectionReason::FromExecution(rejection_error) => {
@@ -619,7 +603,7 @@ impl PendingTransactionResultCache {
                     // We even overwrite the record for transaction which got committed here
                     // because this is a cache for pending transactions, and it can't be re-committed
                     record.track_attempt(TransactionAttempt {
-                        rejection: Some(MempoolRejectionReason::AlreadyCommitted(
+                        rejection: Some(MempoolRejectionReason::TransactionIntentAlreadyCommitted(
                             AlreadyCommittedError {
                                 notarized_transaction_hash: *cached_payload_hash,
                                 committed_state_version: committed_transaction.state_version,
@@ -654,7 +638,7 @@ impl PendingTransactionResultCache {
                 *intent_hash,
                 None,
                 TransactionAttempt {
-                    rejection: Some(MempoolRejectionReason::AlreadyCommitted(
+                    rejection: Some(MempoolRejectionReason::TransactionIntentAlreadyCommitted(
                         AlreadyCommittedError {
                             notarized_transaction_hash: *notarized_transaction_hash,
                             committed_state_version: committed_intent_record.state_version,
```

### core-rust/state-manager/src/transaction/validation.rs
```diff
@@ -76,7 +76,7 @@ impl CommittabilityValidator {
                 .expect("transaction of a state version obtained from an index");
 
             return TransactionAttempt {
-                rejection: Some(MempoolRejectionReason::AlreadyCommitted(
+                rejection: Some(MempoolRejectionReason::TransactionIntentAlreadyCommitted(
                     AlreadyCommittedError {
                         notarized_transaction_hash: user_hashes.notarized_transaction_hash,
                         committed_state_version: state_version,
@@ -107,6 +107,7 @@ impl CommittabilityValidator {
                         IntentHash::Transaction(_)
                     )
                 ) {
+                    // Note - this panic protects against the invariant that already_committed_error()
                     panic!(
                         "[INVARIANT VIOLATION] When checking for rejection against a database snapshot, a transaction intent {:?} was not found in the Node's stores, but was reported as committed by the Engine",
                         user_hashes.transaction_intent_hash
```
