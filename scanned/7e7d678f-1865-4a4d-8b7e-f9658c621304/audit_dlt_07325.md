# [?] Removed the dependency on address::tokens by assuming that tokens with reward parameters will receive rewards. Also fixed the underflow issue in MASP 

## Summary
Severity: Unknown
Chain: Namada
Component: anoma/namada
Published: 2024-01-16
Source: https://github.com/namada-net/namada/commit/5874962e60a76e39d429517afd6aebc730ccfaf5
Type: security-commit

## Details
Removed the dependency on address::tokens by assuming that tokens with reward parameters will receive rewards. Also fixed the underflow issue in MASP conversions. Adjusted the unit tests that were working around this issue.

## Patch
### apps/src/lib/config/genesis.rs
```diff
@@ -228,7 +228,7 @@ pub struct TokenAccount {
     #[derivative(PartialOrd = "ignore", Ord = "ignore")]
     pub balances: HashMap<Address, token::Amount>,
     /// Token parameters
-    pub parameters: token::Parameters,
+    pub masp_params: Option<token::MaspParams>,
     /// Token inflation from the last epoch (read + write for every epoch)
     pub last_inflation: token::Amount,
     /// Token shielded ratio from the last epoch (read + write for every epoch)
```

### apps/src/lib/config/genesis/templates.rs
```diff
@@ -209,7 +209,7 @@ pub struct Tokens {
 )]
 pub struct TokenConfig {
     pub denom: Denomination,
-    pub parameters: token::Parameters,
+    pub masp_params: Option<token::MaspParams>,
 }
 
 #[derive(
```

### apps/src/lib/node/ledger/shell/init_chain.rs
```diff
@@ -437,20 +437,22 @@ where
 
     /// Init genesis token accounts
     fn init_token_accounts(&mut self, genesis: &genesis::chain::Finalized) {
-        let masp_rewards = address::tokens();
         for (alias, token) in &genesis.tokens.token {
             tracing::debug!("Initializing token {alias}");
 
             let FinalizedTokenConfig {
                 address,
-                config: TokenConfig { denom, parameters },
+                config: TokenConfig { denom, masp_params },
             } = token;
             // associate a token with its denomination.
             write_denom(&mut self.wl_storage, address, *denom).unwrap();
-            parameters.init_storage(address, &mut self.wl_storage);
-            // add token addresses to the masp reward conversions lookup table.
-            let alias = alias.to_string();
-            if masp_rewards.contains_key(&alias.as_str()) {
+            self.wl_storage
+                .write(&token::minted_balance_key(address), token::Amount::zero())
+                .expect("The total minted balance key must initialized");
+            if let Some(masp_params) = masp_params {
+                masp_params.init_storage(address, &mut self.wl_storage);
+                // add token addresses to the masp reward conversions lookup table.
+                let alias = alias.to_string();
                 self.wl_storage
                     .storage
                     .conversion_state
```

### apps/src/lib/node/ledger/shell/mod.rs
```diff
@@ -2133,48 +2133,6 @@ mod test_utils {
             .init_storage(&mut shell.wl_storage)
             .expect("Test failed");
         // make wl_storage to update conversion for a new epoch
-        let token_params = token::Parameters {
-            max_reward_rate: Default::default(),
-            kd_gain_nom: Default::default(),
-            kp_gain_nom: Default::default(),
-            locked_ratio_target: Default::default(),
-        };
-        // Insert a map assigning random addresses to each token alias.
-        // Needed for storage but not for this test.
-        for (token, _) in address::tokens() {
-            let addr = address::gen_deterministic_established_address(token);
-            token_params.init_storage(&addr, &mut shell.wl_storage);
-            shell
-                .wl_storage
-                .write(&token::minted_balance_key(&addr), token::Amount::zero())
-                .unwrap();
-            shell
-                .wl_storage
-                .storage
-                .conversion_state
-                .tokens
-                .insert(token.to_string(), addr);
-        }
-        shell.wl_storage.storage.conversion_state.tokens.insert(
-            "nam".to_string(),
-            shell.wl_storage.storage.native_token.clone(),
-        );
-        token_params.init_storage(
-            &shell.wl_storage.storage.native_token.clone(),
-            &mut shell.wl_storage,
-        );
-        // final adjustments so that updating allowed conversions doesn't panic
-        // with divide by zero
-        shell
-            .wl_storage
-            .write(
-                &token::minted_balance_key(
-                    &shell.wl_storage.storage.native_token.clone(),
-                ),
-                token::Amount::zero(),
-            )
-            .unwrap();
-        shell.wl_storage.storage.conversion_state.normed_inflation = Some(1);
         update_allowed_conversions(&mut shell.wl_storage)
             .expect("update conversions failed");
         shell.wl_storage.commit_block().expect("commit failed");
```

### apps/src/lib/node/ledger/storage/mod.rs
```diff
@@ -69,7 +69,7 @@ mod tests {
     use namada::types::keccak::KeccakHash;
     use namada::types::storage::{BlockHash, BlockHeight, Key};
     use namada::types::time::DurationSecs;
-    use namada::types::{address, storage, token};
+    use namada::types::{address, storage};
     use proptest::collection::vec;
     use proptest::prelude::*;
     use proptest::test_runner::Config;
@@ -182,45 +182,6 @@ mod tests {
             .new_epoch(BlockHeight(100));
         // make wl_storage to update conversion for a new epoch
 
-        let token_params = token::Parameters {
-            max_reward_rate: Default::default(),
-            kd_gain_nom: Default::default(),
-            kp_gain_nom: Default::default(),
-            locked_ratio_target: Default::default(),
-        };
-        // Insert a map assigning random addresses to each token alias.
-        // Needed for storage but not for this test.
-        for (token, _) in address::tokens() {
-            let addr = address::gen_deterministic_established_address(token);
-            token_params.init_storage(&addr, &mut wl_storage);
-            wl_storage
-                .write(&token::minted_balance_key(&addr), token::Amount::zero())
-                .unwrap();
-            wl_storage
-                .storage
-                .conversion_state
-                .tokens
-                .insert(token.to_string(), addr);
-        }
-        wl_storage
-            .storage
-            .conversion_state
-            .tokens
-            .insert("nam".to_string(), wl_storage.storage.native_token.clone());
-        token_params.init_storage(
-            &wl_storage.storage.native_token.clone(),
-            &mut wl_storage,
-        );
-
-        wl_storage
-            .write(
-                &token::minted_balance_key(
-                    &wl_storage.storage.native_token.clone(),
-                ),
-                token::Amount::zero(),
-            )
-            .unwrap();
-        wl_storage.storage.conversion_state.normed_inflation = Some(1);
         update_allowed_conversions(&mut wl_storage)
             .expect("update conversions failed");
         wl_storage.commit_block().expect("commit failed");
```

### core/src/ledger/masp_conversions.rs
```diff
@@ -411,7 +411,7 @@ where
         .enumerate()
         .collect();
     // ceil(assets.len() / num_threads)
-    let notes_per_thread_max = (assets.len() - 1) / num_threads + 1;
+    let notes_per_thread_max = (assets.len() + num_threads - 1) / num_threads;
     // floor(assets.len() / num_threads)
     let notes_per_thread_min = assets.len() / num_threads;
     // Now on each core, add the latest conversion to each conversion
@@ -561,7 +561,7 @@ mod tests {
             params.init_storage(&mut s).unwrap();
 
             // Tokens
-            let token_params = token::Parameters {
+            let token_params = token::MaspParams {
                 max_reward_rate: Dec::from_str("0.1").unwrap(),
                 kp_gain_nom: Dec::from_str("0.1").unwrap(),
                 kd_gain_nom: Dec::from_str("0.1").unwrap(),
```

### core/src/types/token.rs
```diff
@@ -1112,7 +1112,7 @@ pub fn masp_locked_ratio_target_key(token_addr: &Address) -> Key {
     Deserialize,
     Serialize,
 )]
-pub struct Parameters {
+pub struct MaspParams {
     /// Maximum reward rate
     pub max_reward_rate: Dec,
     /// Shielded Pool nominal derivative gain
@@ -1123,7 +1123,7 @@ pub struct Parameters {
     pub locked_ratio_target: Dec,
 }
 
-impl Parameters {
+impl MaspParams {
     /// Initialize parameters for the token in storage during the genesis block.
     pub fn init_storage<DB, H>(
         &self,
@@ -1161,13 +1161,10 @@ impl Parameters {
         wl_storage
             .write(&masp_kd_gain_key(address), kd_gain_nom)
             .expect("The nominal derivative gain must be initialized");
-        wl_storage
-            .write(&minted_balance_key(address), Amount::zero())
-            .expect("The total minted balance key must initialized");
     }
 }
 
-impl Default for Parameters {
+impl Default for MaspParams {
     fn default() -> Self {
         Self {
             max_reward_rate: Dec::from_str("0.1").unwrap(),
```

### genesis/localnet/tokens.toml
```diff
@@ -3,7 +3,7 @@
 [token.NAM]
 denom = 6
 
-[token.NAM.parameters]
+[token.NAM.masp_params]
 max_reward_rate = "0.1"
 kd_gain_nom = "0.1"
 kp_gain_nom = "0.1"
@@ -12,7 +12,7 @@ locked_ratio_target = "0.6667"
 [token.BTC]
 denom = 8
 
-[token.BTC.parameters]
+[token.BTC.masp_params]
 max_reward_rate = "0.1"
 kd_gain_nom = "0.1"
 kp_gain_nom = "0.1"
@@ -21,7 +21,7 @@ locked_ratio_target = "0.6667"
 [token.ETH]
 denom = 18
 
-[token.ETH.parameters]
+[token.ETH.masp_params]
 max_reward_rate = "0.1"
 kd_gain_nom = "0.1"
 kp_gain_nom = "0.1"
@@ -30,7 +30,7 @@ locked_ratio_target = "0.6667"
 [token.DOT]
 denom = 10
 
-[token.DOT.parameters]
+[token.DOT.masp_params]
 max_reward_rate = "0.1"
 kd_gain_nom = "0.1"
 kp_gain_nom = "0.1"
@@ -39,7 +39,7 @@ locked_ratio_target = "0.6667"
 [token.Schnitzel]
 denom = 6
 
-[token.Schnitzel.parameters]
+[token.Schnitzel.masp_params]
 max_reward_rate = "0.1"
 kd_gain_nom = "0.1"
 kp_gain_nom = "0.1"
@@ -48,7 +48,7 @@ locked_ratio_target = "0.6667"
 [token.Apfel]
 denom = 6
 
-[token.Apfel.parameters]
+[token.Apfel.masp_params]
 max_reward_rate = "0.1"
 kd_gain_nom = "0.1"
 kp_gain_nom = "0.1"
@@ -57,7 +57,7 @@ locked_ratio_target = "0.6667"
 [token.Kartoffel]
 denom = 6
 
-[token.Kartoffel.parameters]
+[token.Kartoffel.masp_params]
 max_reward_rate = "0.1"
 kd_gain_nom = "0.1"
 kp_gain_nom = "0.1"
```

### genesis/starter/tokens.toml
```diff
@@ -4,7 +4,7 @@
 vp = "vp_token"
 denom = 6
 
-[token.NAM.parameters]
+[token.NAM.masp_params]
 max_reward_rate = "0.1"
 kd_gain_nom = "0.1"
 kp_gain_nom = "0.1"
```
