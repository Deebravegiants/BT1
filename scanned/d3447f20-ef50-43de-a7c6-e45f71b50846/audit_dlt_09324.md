# [?] fix: don't panic when iterating over script sequence txs (#7179)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-02-19
Source: https://github.com/foundry-rs/foundry/commit/a2a6bcd18c89eb31347a64120b3aef1abc86840a
Type: security-commit

## Details
fix: don't panic when iterating over script sequence txs (#7179)

## Patch
### crates/evm/evm/src/executors/invariant/mod.rs
```diff
@@ -153,8 +153,7 @@ impl<'a> InvariantExecutor<'a> {
             let mut created_contracts = vec![];
 
             for current_run in 0..self.config.depth {
-                let (sender, (address, calldata)) =
-                    inputs.last().expect("to have the next randomly generated input.");
+                let (sender, (address, calldata)) = inputs.last().expect("no input generated");
 
                 // Executes the call from the randomly generated sequence.
                 let call_result = executor
```

### crates/forge/bin/cmd/script/broadcast.rs
```diff
@@ -46,9 +46,8 @@ impl ScriptArgs {
         if already_broadcasted < deployment_sequence.transactions.len() {
             let required_addresses: HashSet<Address> = deployment_sequence
                 .typed_transactions()
-                .into_iter()
                 .skip(already_broadcasted)
-                .map(|(_, tx)| (*tx.from().expect("No sender for onchain transaction!")).to_alloy())
+                .map(|tx| (*tx.from().expect("No sender for onchain transaction!")).to_alloy())
                 .collect();
 
             let (send_kind, chain) = if self.unlocked {
@@ -61,8 +60,7 @@ impl ScriptArgs {
                 senders.extend(
                     deployment_sequence
                         .typed_transactions()
-                        .iter()
-                        .filter_map(|(_, tx)| tx.from().copied().map(|addr| addr.to_alloy())),
+                        .filter_map(|tx| tx.from().copied().map(|addr| addr.to_alloy())),
                 );
                 (SendTransactionsKind::Unlocked(senders), chain.as_u64())
             } else {
@@ -324,7 +322,7 @@ impl ScriptArgs {
                     }
                 } else if self.broadcast {
                     self.single_deployment(
-                        deployments.first_mut().expect("to be set."),
+                        deployments.first_mut().expect("missing deployment"),
                         script_config,
                         libraries,
                         result,
```

### crates/forge/bin/cmd/script/multi.rs
```diff
@@ -199,9 +199,8 @@ impl ScriptArgs {
                 .deployments
                 .iter_mut()
                 .map(|sequence| async move {
-                    let provider = Arc::new(get_http_provider(
-                        sequence.typed_transactions().first().unwrap().0.clone(),
-                    ));
+                    let rpc_url = sequence.rpc_url().unwrap();
+                    let provider = Arc::new(get_http_provider(rpc_url));
                     receipts::wait_for_pending(provider, sequence).await
                 })
                 .collect::<Vec<_>>();
@@ -219,14 +218,8 @@ impl ScriptArgs {
         let mut results: Vec<Result<(), Report>> = Vec::new();
 
         for sequence in deployments.deployments.iter_mut() {
-            let result = match self
-                .send_transactions(
-                    sequence,
-                    &sequence.typed_transactions().first().unwrap().0.clone(),
-                    &script_wallets,
-                )
-                .await
-            {
+            let rpc_url = sequence.rpc_url().unwrap().to_string();
+            let result = match self.send_transactions(sequence, &rpc_url, &script_wallets).await {
                 Ok(_) if self.verify => sequence.verify_contracts(config, verify.clone()).await,
                 Ok(_) => Ok(()),
                 Err(err) => Err(err),
```

### crates/forge/bin/cmd/script/sequence.rs
```diff
@@ -353,14 +353,14 @@ impl ScriptSequence {
         }
     }
 
+    /// Returns the first RPC URL of this sequence.
+    pub fn rpc_url(&self) -> Option<&str> {
+        self.transactions.front().and_then(|tx| tx.rpc.as_deref())
+    }
+
     /// Returns the list of the transactions without the metadata.
-    pub fn typed_transactions(&self) -> Vec<(String, &TypedTransaction)> {
-        self.transactions
-            .iter()
-            .map(|tx| {
-                (tx.rpc.clone().expect("to have been filled with a proper rpc"), tx.typed_tx())
-            })
-            .collect()
+    pub fn typed_transactions(&self) -> impl Iterator<Item = &TypedTransaction> {
+        self.transactions.iter().map(|tx| tx.typed_tx())
     }
 
     pub fn fill_sensitive(&mut self, sensitive: &SensitiveScriptSequence) {
```
