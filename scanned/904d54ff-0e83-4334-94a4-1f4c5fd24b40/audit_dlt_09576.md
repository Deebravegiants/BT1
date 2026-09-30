# [?] Fix dev mode crash.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-05-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/90a4d9e7754b7cdde1d4ae43e7998220842e5419
Type: security-commit

## Details
Fix dev mode crash.

## Patch
### client/src/configuration.rs
```diff
@@ -1117,6 +1117,19 @@ impl Configuration {
             } else {
                 u64::MAX
             };
+        // This is to set the default transition time for the CIPs that cannot
+        // be enabled in the genesis.
+        let non_genesis_default_transition_time =
+            match self.raw_conf.default_transition_time {
+                Some(num) if num > 0 => num,
+                _ => {
+                    if self.is_test_or_dev_mode() {
+                        1u64
+                    } else {
+                        u64::MAX
+                    }
+                }
+            };
 
         if self.is_test_or_dev_mode() {
             params.early_set_internal_contracts_states = true;
@@ -1138,7 +1151,7 @@ impl Configuration {
         params.transition_numbers.cip94 = self
             .raw_conf
             .dao_vote_transition_number
-            .unwrap_or(default_transition_time);
+            .unwrap_or(non_genesis_default_transition_time);
         if self.is_test_or_dev_mode() {
             params.transition_numbers.cip43b =
                 self.raw_conf.cip43_init_end_number.unwrap_or(u64::MAX);
@@ -1195,7 +1208,7 @@ impl Configuration {
         params.transition_heights.cip94 = self
             .raw_conf
             .dao_vote_transition_height
-            .unwrap_or(default_transition_time);
+            .unwrap_or(non_genesis_default_transition_time);
         params.params_dao_vote_period = self.raw_conf.params_dao_vote_period;
 
         let mut base_block_rewards = BTreeMap::new();
```

### internal_contract/contracts/ParamsControl.sol
```diff
@@ -3,7 +3,7 @@ pragma solidity >=0.4.15;
 
 contract ParamsControl {
     struct Vote {
-        uint8 index;
+        uint16 index;
         uint256[3] votes;
     }
 
```

### tests/dev_mode_test.py
```diff
@@ -19,6 +19,7 @@ def run_test(self):
         tx = rpc.new_tx()
         tx_hash = rpc.send_tx(tx)
         wait_until(lambda: checktx(self.nodes[0], tx_hash))
+        rpc.generate_empty_blocks(1000)
 
 
 if __name__ == '__main__':
```
