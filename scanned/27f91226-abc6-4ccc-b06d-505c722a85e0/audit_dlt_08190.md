# [?] test-validator: fix block subscription flag panic (#13322)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-09-20
Source: https://github.com/anza-xyz/agave/commit/9a7dc06800e6ad36561627b9e7cb7c3461c096e0
Type: security-commit

## Details
test-validator: fix block subscription flag panic (#13322)

* fix: block subscription flag panic in solana-test-validator

* nit fix

## Patch
### validator/src/commands/run/args/pub_sub_config.rs
```diff
@@ -68,12 +68,22 @@ pub(crate) fn args<'a, 'b>(test_validator: bool) -> Vec<Arg<'a, 'b>> {
         )
     };
 
+    let rpc_pubsub_enable_block_sub_value = Arg::with_name("rpc_pubsub_enable_block_subscription")
+        .long("rpc-pubsub-enable-block-subscription")
+        .takes_value(false)
+        .help("Enable the unstable RPC PubSub `blockSubscribe` subscription");
+
+    // enable_rpc_transaction_history is on by default in the configs
+    // for test_validator, while required by agave_validator if
+    // rpc_pubsub_enable_block_subscription is passed
+    let rpc_pubsub_enable_block_sub_value = if !test_validator {
+        rpc_pubsub_enable_block_sub_value.requires("enable_rpc_transaction_history")
+    } else {
+        rpc_pubsub_enable_block_sub_value
+    };
+
     vec![
-        Arg::with_name("rpc_pubsub_enable_block_subscription")
-            .long("rpc-pubsub-enable-block-subscription")
-            .requires("enable_rpc_transaction_history")
-            .takes_value(false)
-            .help("Enable the unstable RPC PubSub `blockSubscribe` subscription"),
+        rpc_pubsub_enable_block_sub_value,
         Arg::with_name("rpc_pubsub_enable_vote_subscription")
             .long("rpc-pubsub-enable-vote-subscription")
             .takes_value(false)
```
