# [?] fix(script): don't panic when a broadcast sequence and its sensitive-cache file desync (#16580)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-08
Source: https://github.com/foundry-rs/foundry/commit/e970012209796144ae3934adc09849c3fc5a2665
Type: security-commit

## Details
fix(script): don't panic when a broadcast sequence and its sensitive-cache file desync (#16580)

* fix(script): don't panic when a broadcast sequence and its sensitive-cache file desync

fill_sensitive() indexed sensitive.transactions[i] directly with no bounds
check. save() writes the broadcast file then the sensitive-cache file as two
separate writes; an interruption between the two (Ctrl-C, disk full) leaves
them with a different number of entries, and the next load() panicked on the
out-of-bounds index instead of erroring.

Fixed to validate the entry counts match exactly before any mutation -
catching both a shorter AND a longer cache, not just the shorter case, and
never partially filling transactions before reporting the mismatch. The same
bug shape existed one level up in multi_sequence.rs::load() for multi-chain
deployments, fixed the same way.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

* Update crates/script-sequence/src/sequence.rs

* Update crates/script-sequence/src/sequence.rs

* Update crates/script-sequence/src/sequence.rs

* fix(script): clarify cache mismatch recovery

Shorten the added explanations while preserving the relevant invariants. Correct release metadata and recovery coverage where needed.

---------

Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>
Co-authored-by: figtracer <me@figtracer.com>
Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>

## Patch
### .changelog/fix-script-sequence-desync-panic.md
```diff
@@ -0,0 +1,7 @@
+---
+forge: patch
+forge-script: patch
+forge-script-sequence: patch
+---
+
+Return an error when broadcast files and their sensitive caches have mismatched entry counts.
```

### crates/script-sequence/src/sequence.rs
```diff
@@ -104,7 +104,9 @@ impl<N: Network> ScriptSequence<N> {
         )
         .wrap_err(format!("Deployment's sensitive details not found for chain `{chain_id}`."))?;
 
-        script_sequence.fill_sensitive(&sensitive_script_sequence);
+        script_sequence.fill_sensitive(&sensitive_script_sequence).wrap_err(format!(
+            "Deployment's sensitive details are out of sync with the broadcast file for chain `{chain_id}`; restore matching broadcast and sensitive-cache files before resuming."
+        ))?;
 
         script_sequence.paths = Some((path, sensitive_path));
 
@@ -233,11 +235,21 @@ impl<N: Network> ScriptSequence<N> {
         self.transactions.iter().map(|tx| tx.tx())
     }
 
-    pub fn fill_sensitive(&mut self, sensitive: &SensitiveScriptSequence) {
-        self.transactions
-            .iter_mut()
-            .enumerate()
-            .for_each(|(i, tx)| tx.rpc.clone_from(&sensitive.transactions[i].rpc));
+    /// Copies RPC URLs from a matching sensitive-cache sequence.
+    pub fn fill_sensitive(&mut self, sensitive: &SensitiveScriptSequence) -> Result<()> {
+        let transactions_len = self.transactions.len();
+        let sensitive_len = sensitive.transactions.len();
+        if transactions_len != sensitive_len {
+            eyre::bail!(
+                "sensitive-cache entry count ({sensitive_len}) does not match transaction count \
+                 ({transactions_len}); the broadcast file and its sensitive-cache counterpart are \
+                 out of sync"
+            );
+        }
+        for (i, tx) in self.transactions.iter_mut().enumerate() {
+            tx.rpc.clone_from(&sensitive.transactions[i].rpc);
+        }
+        Ok(())
     }
 }
 
@@ -269,6 +281,58 @@ pub fn now() -> Duration {
 #[cfg(test)]
 mod tests {
     use super::*;
+    use alloy_network::Ethereum;
+
+    fn sequence_with_two_transactions() -> ScriptSequence<Ethereum> {
+        let mut sequence = ScriptSequence::default();
+        for rpc in ["first", "second"] {
+            let mut tx = TransactionWithMetadata::from_tx_request(
+                TransactionMaybeSigned::Unsigned(Default::default()),
+            );
+            tx.rpc = rpc.to_string();
+            sequence.transactions.push_back(tx);
+        }
+        sequence
+    }
+
+    #[test]
+    fn fill_sensitive_rejects_mismatched_counts_without_mutation() {
+        for count in [1, 3] {
+            let mut sequence = sequence_with_two_transactions();
+            let sensitive = SensitiveScriptSequence {
+                transactions: (0..count)
+                    .map(|_| SensitiveTransactionMetadata { rpc: "replacement".to_string() })
+                    .collect(),
+            };
+            assert_eq!(
+                sequence.fill_sensitive(&sensitive).unwrap_err().to_string(),
+                format!(
+                    "sensitive-cache entry count ({count}) does not match transaction count (2); \
+                     the broadcast file and its sensitive-cache counterpart are out of sync"
+                )
+            );
+            assert_eq!(
+                sequence.transactions.iter().map(|tx| tx.rpc.as_str()).collect::<Vec<_>>(),
+                ["first", "second"]
+            );
+        }
+    }
+
+    #[test]
+    fn fill_sensitive_restores_matching_cache() {
+        let mut sequence = sequence_with_two_transactions();
+        let sensitive = SensitiveScriptSequence {
+            transactions: ["restored-first", "restored-second"]
+                .into_iter()
+                .map(|rpc| SensitiveTransactionMetadata { rpc: rpc.to_string() })
+                .collect(),
+        };
+        sequence.fill_sensitive(&sensitive).unwrap();
+        assert_eq!(
+            sequence.transactions.iter().map(|tx| tx.rpc.as_str()).collect::<Vec<_>>(),
+            ["restored-first", "restored-second"]
+        );
+    }
 
     #[test]
     fn can_convert_sig() {
```

### crates/script/src/multi_sequence.rs
```diff
@@ -104,9 +104,18 @@ impl<N: Network> MultiChainSequence<N> {
             foundry_compilers::utils::read_json_file(&sensitive_path)
                 .wrap_err("Multi-chain deployment sensitive details not found.")?;
 
-        sequence.deployments.iter_mut().enumerate().for_each(|(i, sequence)| {
-            sequence.fill_sensitive(&sensitive_sequence.deployments[i]);
-        });
+        let deployments_len = sequence.deployments.len();
+        let sensitive_deployments_len = sensitive_sequence.deployments.len();
+        if deployments_len != sensitive_deployments_len {
+            eyre::bail!(
+                "sensitive-cache deployment count ({sensitive_deployments_len}) does not match \
+                 deployment count ({deployments_len}); the multi-chain deployment and its \
+                 sensitive-cache counterpart are out of sync"
+            );
+        }
+        for (i, deployment) in sequence.deployments.iter_mut().enumerate() {
+            deployment.fill_sensitive(&sensitive_sequence.deployments[i])?;
+        }
 
         sequence.path = path;
         sequence.sensitive_path = sensitive_path;
@@ -168,3 +177,52 @@ impl<N: Network> MultiChainSequence<N> {
         Ok(())
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use alloy_network::Ethereum;
+
+    #[test]
+    fn load_rejects_mismatched_deployment_counts() {
+        let dir = tempfile::tempdir().unwrap();
+        let config = Config {
+            broadcast: dir.path().join("broadcast"),
+            cache_path: dir.path().join("cache"),
+            ..Default::default()
+        };
+        let target = ArtifactId {
+            path: PathBuf::from("Script.json"),
+            name: "Script".to_string(),
+            source: PathBuf::from("Script.sol"),
+            version: "0.8.30".parse().unwrap(),
+            build_id: String::new(),
+            profile: "default".to_string(),
+        };
+        let (path, sensitive_path) =
+            MultiChainSequence::<Ethereum>::get_paths(&config, "run()", &target, false).unwrap();
+        let sequence = MultiChainSequence::<Ethereum> {
+            deployments: vec![ScriptSequence::default()],
+            path: PathBuf::new(),
+            sensitive_path: PathBuf::new(),
+            timestamp: 0,
+        };
+        fs::write_pretty_json_file(&path, &sequence).unwrap();
+        for count in [0, 2] {
+            let sensitive = SensitiveMultiChainSequence {
+                deployments: vec![SensitiveScriptSequence::default(); count],
+            };
+            fs::write_sensitive_json_file(&sensitive_path, &sensitive).unwrap();
+            let err = MultiChainSequence::<Ethereum>::load(&config, "run()", &target, false)
+                .err()
+                .expect("mismatched counts must fail");
+            assert_eq!(
+                err.to_string(),
+                format!(
+                    "sensitive-cache deployment count ({count}) does not match deployment count (1); \
+                     the multi-chain deployment and its sensitive-cache counterpart are out of sync"
+                )
+            );
+        }
+    }
+}
```
