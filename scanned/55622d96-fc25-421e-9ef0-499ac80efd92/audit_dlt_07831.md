# [?] Fix Eth1 data underflow (#977)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2020-04-06
Source: https://github.com/sigp/lighthouse/commit/c188227cc264d0e821708ba0cba83aa62130f9d5
Type: security-commit

## Details
Fix Eth1 data underflow (#977)

* Fix Eth1 data underflow #540

* Refactor: smart transformation from Option to Result

* Add tests for BeaconState::get_outstanding_deposit_len()

## Patch
### eth2/state_processing/src/per_block_processing.rs
```diff
@@ -417,7 +417,7 @@ pub fn process_deposits<T: EthSpec>(
 ) -> Result<(), BlockProcessingError> {
     let expected_deposit_len = std::cmp::min(
         T::MaxDeposits::to_u64(),
-        state.eth1_data.deposit_count - state.eth1_deposit_index,
+        state.get_outstanding_deposit_len()?,
     );
     block_verify!(
         deposits.len() as u64 == expected_deposit_len,
```

### eth2/types/src/beacon_state.rs
```diff
@@ -71,6 +71,10 @@ pub enum Error {
     InvalidValidatorPubkey(ssz::DecodeError),
     ValidatorRegistryShrunk,
     TreeHashCacheInconsistent,
+    InvalidDepositState {
+        deposit_count: u64,
+        deposit_index: u64,
+    },
 }
 
 /// Control whether an epoch-indexed field can be indexed at the next epoch or not.
@@ -766,6 +770,19 @@ impl<T: EthSpec> BeaconState<T> {
         })
     }
 
+    /// Get the number of outstanding deposits.
+    ///
+    /// Returns `Err` if the state is invalid.
+    pub fn get_outstanding_deposit_len(&self) -> Result<u64, Error> {
+        self.eth1_data
+            .deposit_count
+            .checked_sub(self.eth1_deposit_index)
+            .ok_or_else(|| Error::InvalidDepositState {
+                deposit_count: self.eth1_data.deposit_count,
+                deposit_index: self.eth1_deposit_index,
+            })
+    }
+
     /// Build all the caches, if they need to be built.
     pub fn build_all_caches(&mut self, spec: &ChainSpec) -> Result<(), Error> {
         self.build_all_committee_caches(spec)?;
```

### eth2/types/src/beacon_state/tests.rs
```diff
@@ -365,3 +365,44 @@ mod committees {
         committee_consistency_test_suite::<MinimalEthSpec>(RelativeEpoch::Next);
     }
 }
+
+mod get_outstanding_deposit_len {
+    use super::*;
+    use crate::MinimalEthSpec;
+    use crate::test_utils::TestingBeaconStateBuilder;
+
+    fn state() -> BeaconState<MinimalEthSpec> {
+        let spec = MinimalEthSpec::default_spec();
+        let builder: TestingBeaconStateBuilder<MinimalEthSpec> =
+            TestingBeaconStateBuilder::from_default_keypairs_file_if_exists(16, &spec);
+        let (state, _keypairs) = builder.build();
+
+        state
+    }
+
+    #[test]
+    fn returns_ok() {
+        let mut state = state();
+        assert_eq!(state.get_outstanding_deposit_len(), Ok(0));
+
+        state.eth1_data.deposit_count = 17;
+        state.eth1_deposit_index = 16;
+        assert_eq!(state.get_outstanding_deposit_len(), Ok(1));
+    }
+
+    #[test]
+    fn returns_err_if_the_state_is_invalid() {
+        let mut state = state();
+        // The state is invalid, deposit count is lower than deposit index.
+        state.eth1_data.deposit_count = 16;
+        state.eth1_deposit_index = 17;
+
+        assert_eq!(
+            state.get_outstanding_deposit_len(),
+            Err(BeaconStateError::InvalidDepositState {
+                deposit_count: 16,
+                deposit_index: 17,
+            })
+        );
+    }
+}
```
