# [?] config to disable randomness in a chain halt (#12953)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-04-23
Source: https://github.com/aptos-labs/aptos-core/commit/381ec5bf2847ba3d0a4cc70d7fd913bb7b3d6c69
Type: security-commit

## Details
config to disable randomness in a chain halt (#12953)

* initial

update

update

update

update

update

lint

cleanup

* fix tests

## Patch
### aptos-move/framework/aptos-framework/doc/overview.md
```diff
@@ -47,6 +47,7 @@ This is the reference documentation of the Aptos framework.
 -  [`0x1::primary_fungible_store`](primary_fungible_store.md#0x1_primary_fungible_store)
 -  [`0x1::randomness`](randomness.md#0x1_randomness)
 -  [`0x1::randomness_config`](randomness_config.md#0x1_randomness_config)
+-  [`0x1::randomness_config_seqnum`](randomness_config_seqnum.md#0x1_randomness_config_seqnum)
 -  [`0x1::reconfiguration`](reconfiguration.md#0x1_reconfiguration)
 -  [`0x1::reconfiguration_state`](reconfiguration_state.md#0x1_reconfiguration_state)
 -  [`0x1::reconfiguration_with_dkg`](reconfiguration_with_dkg.md#0x1_reconfiguration_with_dkg)
```

### aptos-move/framework/aptos-framework/doc/randomness_config_seqnum.md
```diff
@@ -0,0 +1,142 @@
+
+<a id="0x1_randomness_config_seqnum"></a>
+
+# Module `0x1::randomness_config_seqnum`
+
+Randomness stall recovery utils.
+
+When randomness generation is stuck due to a bug, the chain is also stuck. Below is the recovery procedure.
+1. Ensure more than 2/3 stakes are stuck at the same version.
+1. Every validator restarts with <code>randomness_override_seq_num</code> set to <code>X+1</code> in the node config file,
+where <code>X</code> is the current <code><a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a></code> on chain.
+1. The chain should then be unblocked.
+1. Once the bug is fixed and the binary + framework have been patched,
+a governance proposal is needed to set <code><a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a></code> to be <code>X+2</code>.
+
+
+-  [Resource `RandomnessConfigSeqNum`](#0x1_randomness_config_seqnum_RandomnessConfigSeqNum)
+-  [Function `set_for_next_epoch`](#0x1_randomness_config_seqnum_set_for_next_epoch)
+-  [Function `initialize`](#0x1_randomness_config_seqnum_initialize)
+-  [Function `on_new_epoch`](#0x1_randomness_config_seqnum_on_new_epoch)
+
+
+<pre><code><b>use</b> <a href="config_buffer.md#0x1_config_buffer">0x1::config_buffer</a>;
+<b>use</b> <a href="system_addresses.md#0x1_system_addresses">0x1::system_addresses</a>;
+</code></pre>
+
+
+
+<a id="0x1_randomness_config_seqnum_RandomnessConfigSeqNum"></a>
+
+## Resource `RandomnessConfigSeqNum`
+
+If this seqnum is smaller than a validator local override, the on-chain <code>RandomnessConfig</code> will be ignored.
+Useful in a chain recovery from randomness stall.
+
+
+<pre><code><b>struct</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a> <b>has</b> drop, store, key
+</code></pre>
+
+
+
+<details>
+<summary>Fields</summary>
+
+
+<dl>
+<dt>
+<code>seq_num: u64</code>
+</dt>
+<dd>
+
+</dd>
+</dl>
+
+
+</details>
+
+<a id="0x1_randomness_config_seqnum_set_for_next_epoch"></a>
+
+## Function `set_for_next_epoch`
+
+Update <code><a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a></code>.
+Used when re-enable randomness after an emergency randomness disable via local override.
+
+
+<pre><code><b>public</b> <b>fun</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_set_for_next_epoch">set_for_next_epoch</a>(framework: &<a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>, seq_num: u64)
+</code></pre>
+
+
+
+<details>
+<summary>Implementation</summary>
+
+
+<pre><code><b>public</b> <b>fun</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_set_for_next_epoch">set_for_next_epoch</a>(framework: &<a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>, seq_num: u64) {
+    <a href="system_addresses.md#0x1_system_addresses_assert_aptos_framework">system_addresses::assert_aptos_framework</a>(framework);
+    <a href="config_buffer.md#0x1_config_buffer_upsert">config_buffer::upsert</a>(<a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a> { seq_num });
+}
+</code></pre>
+
+
+
+</details>
+
+<a id="0x1_randomness_config_seqnum_initialize"></a>
+
+## Function `initialize`
+
+Initialize the configuration. Used in genesis or governance.
+
+
+<pre><code><b>public</b> <b>fun</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_initialize">initialize</a>(framework: &<a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>)
+</code></pre>
+
+
+
+<details>
+<summary>Implementation</summary>
+
+
+<pre><code><b>public</b> <b>fun</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_initialize">initialize</a>(framework: &<a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>) {
+    <a href="system_addresses.md#0x1_system_addresses_assert_aptos_framework">system_addresses::assert_aptos_framework</a>(framework);
+    <b>if</b> (!<b>exists</b>&lt;<a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a>&gt;(@aptos_framework)) {
+        <b>move_to</b>(framework, <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a> { seq_num: 0 })
+    }
+}
+</code></pre>
+
+
+
+</details>
+
+<a id="0x1_randomness_config_seqnum_on_new_epoch"></a>
+
+## Function `on_new_epoch`
+
+Only used in reconfigurations to apply the pending <code>RandomnessConfig</code>, if there is any.
+
+
+<pre><code><b>public</b>(<b>friend</b>) <b>fun</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_on_new_epoch">on_new_epoch</a>()
+</code></pre>
+
+
+
+<details>
+<summary>Implementation</summary>
+
+
+<pre><code><b>public</b>(<b>friend</b>) <b>fun</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_on_new_epoch">on_new_epoch</a>() <b>acquires</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a> {
+    <b>if</b> (<a href="config_buffer.md#0x1_config_buffer_does_exist">config_buffer::does_exist</a>&lt;<a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a>&gt;()) {
+        <b>let</b> new_config = <a href="config_buffer.md#0x1_config_buffer_extract">config_buffer::extract</a>&lt;<a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a>&gt;();
+        <b>borrow_global_mut</b>&lt;<a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_RandomnessConfigSeqNum">RandomnessConfigSeqNum</a>&gt;(@aptos_framework).seq_num = new_config.seq_num;
+    }
+}
+</code></pre>
+
+
+
+</details>
+
+
+[move-book]: https://aptos.dev/move/book/SUMMARY
```

### aptos-move/framework/aptos-framework/doc/reconfiguration_with_dkg.md
```diff
@@ -24,6 +24,7 @@ Reconfiguration with DKG helper functions.
 <b>use</b> <a href="jwks.md#0x1_jwks">0x1::jwks</a>;
 <b>use</b> <a href="../../aptos-stdlib/../move-stdlib/doc/option.md#0x1_option">0x1::option</a>;
 <b>use</b> <a href="randomness_config.md#0x1_randomness_config">0x1::randomness_config</a>;
+<b>use</b> <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum">0x1::randomness_config_seqnum</a>;
 <b>use</b> <a href="reconfiguration.md#0x1_reconfiguration">0x1::reconfiguration</a>;
 <b>use</b> <a href="reconfiguration_state.md#0x1_reconfiguration_state">0x1::reconfiguration_state</a>;
 <b>use</b> <a href="stake.md#0x1_stake">0x1::stake</a>;
@@ -100,6 +101,7 @@ Run the default reconfiguration to enter the new epoch.
     std::version::on_new_epoch();
     <a href="jwk_consensus_config.md#0x1_jwk_consensus_config_on_new_epoch">jwk_consensus_config::on_new_epoch</a>();
     <a href="jwks.md#0x1_jwks_on_new_epoch">jwks::on_new_epoch</a>();
+    <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_on_new_epoch">randomness_config_seqnum::on_new_epoch</a>();
     <a href="randomness_config.md#0x1_randomness_config_on_new_epoch">randomness_config::on_new_epoch</a>();
     <a href="../../aptos-stdlib/../move-stdlib/doc/features.md#0x1_features_on_new_epoch">features::on_new_epoch</a>(<a href="account.md#0x1_account">account</a>);
     <a href="reconfiguration.md#0x1_reconfiguration_reconfigure">reconfiguration::reconfigure</a>();
```

### aptos-move/framework/aptos-framework/sources/configs/config_buffer.move
```diff
@@ -24,6 +24,7 @@ module aptos_framework::config_buffer {
     friend aptos_framework::jwks;
     friend aptos_framework::jwk_consensus_config;
     friend aptos_framework::randomness_config;
+    friend aptos_framework::randomness_config_seqnum;
     friend aptos_framework::version;
 
     /// Config buffer operations failed with permission denied.
```

### aptos-move/framework/aptos-framework/sources/configs/randomness_config_seqnum.move
```diff
@@ -0,0 +1,44 @@
+/// Randomness stall recovery utils.
+///
+/// When randomness generation is stuck due to a bug, the chain is also stuck. Below is the recovery procedure.
+/// 1. Ensure more than 2/3 stakes are stuck at the same version.
+/// 1. Every validator restarts with `randomness_override_seq_num` set to `X+1` in the node config file,
+///    where `X` is the current `RandomnessConfigSeqNum` on chain.
+/// 1. The chain should then be unblocked.
+/// 1. Once the bug is fixed and the binary + framework have been patched,
+///    a governance proposal is needed to set `RandomnessConfigSeqNum` to be `X+2`.
+module aptos_framework::randomness_config_seqnum {
+    use aptos_framework::config_buffer;
+    use aptos_framework::system_addresses;
+
+    friend aptos_framework::reconfiguration_with_dkg;
+
+    /// If this seqnum is smaller than a validator local override, the on-chain `RandomnessConfig` will be ignored.
+    /// Useful in a chain recovery from randomness stall.
+    struct RandomnessConfigSeqNum has drop, key, store {
+        seq_num: u64,
+    }
+
+    /// Update `RandomnessConfigSeqNum`.
+    /// Used when re-enable randomness after an emergency randomness disable via local override.
+    public fun set_for_next_epoch(framework: &signer, seq_num: u64) {
+        system_addresses::assert_aptos_framework(framework);
+        config_buffer::upsert(RandomnessConfigSeqNum { seq_num });
+    }
+
+    /// Initialize the configuration. Used in genesis or governance.
+    public fun initialize(framework: &signer) {
+        system_addresses::assert_aptos_framework(framework);
+        if (!exists<RandomnessConfigSeqNum>(@aptos_framework)) {
+            move_to(framework, RandomnessConfigSeqNum { seq_num: 0 })
+        }
+    }
+
+    /// Only used in reconfigurations to apply the pending `RandomnessConfig`, if there is any.
+    public(friend) fun on_new_epoch() acquires RandomnessConfigSeqNum {
+        if (config_buffer::does_exist<RandomnessConfigSeqNum>()) {
+            let new_config = config_buffer::extract<RandomnessConfigSeqNum>();
+            borrow_global_mut<RandomnessConfigSeqNum>(@aptos_framework).seq_num = new_config.seq_num;
+        }
+    }
+}
```

### aptos-move/framework/aptos-framework/sources/reconfiguration_with_dkg.move
```diff
@@ -9,6 +9,7 @@ module aptos_framework::reconfiguration_with_dkg {
     use aptos_framework::jwk_consensus_config;
     use aptos_framework::jwks;
     use aptos_framework::randomness_config;
+    use aptos_framework::randomness_config_seqnum;
     use aptos_framework::reconfiguration;
     use aptos_framework::reconfiguration_state;
     use aptos_framework::stake;
@@ -47,6 +48,7 @@ module aptos_framework::reconfiguration_with_dkg {
         std::version::on_new_epoch();
         jwk_consensus_config::on_new_epoch();
         jwks::on_new_epoch();
+        randomness_config_seqnum::on_new_epoch();
         randomness_config::on_new_epoch();
         features::on_new_epoch(account);
         reconfiguration::reconfigure();
```

### aptos-move/vm-genesis/src/lib.rs
```diff
@@ -65,6 +65,7 @@ const JWK_CONSENSUS_CONFIG_MODULE_NAME: &str = "jwk_consensus_config";
 const JWKS_MODULE_NAME: &str = "jwks";
 const CONFIG_BUFFER_MODULE_NAME: &str = "config_buffer";
 const DKG_MODULE_NAME: &str = "dkg";
+const RANDOMNESS_CONFIG_SEQNUM_MODULE_NAME: &str = "randomness_config_seqnum";
 const RANDOMNESS_CONFIG_MODULE_NAME: &str = "randomness_config";
 const RANDOMNESS_MODULE_NAME: &str = "randomness";
 const RECONFIGURATION_STATE_MODULE_NAME: &str = "reconfiguration_state";
@@ -285,6 +286,7 @@ pub fn encode_genesis_change_set(
         .randomness_config_override
         .clone()
         .unwrap_or_else(OnChainRandomnessConfig::default_for_genesis);
+    initialize_randomness_config_seqnum(&mut session);
     initialize_randomness_config(&mut session, randomness_config);
     initialize_randomness_resources(&mut session);
     initialize_on_chain_governance(&mut session, genesis_config);
@@ -505,6 +507,16 @@ fn initialize_dkg(session: &mut SessionExt) {
     );
 }
 
+fn initialize_randomness_config_seqnum(session: &mut SessionExt) {
+    exec_function(
+        session,
+        RANDOMNESS_CONFIG_SEQNUM_MODULE_NAME,
+        "initialize",
+        vec![],
+        serialize_values(&vec![MoveValue::Signer(CORE_CODE_ADDRESS)]),
+    );
+}
+
 fn initialize_randomness_config(
     session: &mut SessionExt,
     randomness_config: OnChainRandomnessConfig,
```

### aptos-node/src/lib.rs
```diff
@@ -737,6 +737,7 @@ pub fn setup_environment_and_start_node(
                 dkg_start_events,
                 vtxn_pool.clone(),
                 rb_config,
+                node_config.randomness_override_seq_num,
             );
             Some(dkg_runtime)
         },
```

### config/src/config/node_config.rs
```diff
@@ -71,6 +71,10 @@ pub struct NodeConfig {
     pub node_startup: NodeStartupConfig,
     #[serde(default)]
     pub peer_monitoring_service: PeerMonitoringServiceConfig,
+    /// In a randomness stall, set this to be on-chain `RandomnessConfigSeqNum` + 1.
+    /// Once enough nodes restarted with the new value, the chain should unblock with randomness disabled.
+    #[serde(default)]
+    pub randomness_override_seq_num: u64,
     #[serde(default)]
     pub state_sync: StateSyncConfig,
     #[serde(default)]
```

### consensus/src/epoch_manager.rs
```diff
@@ -86,7 +86,8 @@ use aptos_types::{
     on_chain_config::{
         Features, LeaderReputationType, OnChainConfigPayload, OnChainConfigProvider,
         OnChainConsensusConfig, OnChainExecutionConfig, OnChainJWKConsensusConfig,
-        OnChainRandomnessConfig, ProposerElectionType, RandomnessConfigMoveStruct, ValidatorSet,
+        OnChainRandomnessConfig, ProposerElectionType, RandomnessConfigMoveStruct,
+        RandomnessConfigSeqNum, ValidatorSet,
     },
     randomness::{RandKeys, WvufPP, WVUF},
     validator_signer::ValidatorSigner,
@@ -133,6 +134,7 @@ pub struct EpochManager<P: OnChainConfigProvider> {
     config: ConsensusConfig,
     #[allow(unused)]
     execution_config: ExecutionConfig,
+    randomness_override_seq_num: u64,
     time_service: Arc<dyn TimeService>,
     self_sender: aptos_channels::UnboundedSender<Event<ConsensusMsg>>,
     network_sender: ConsensusNetworkClient<NetworkClient<ConsensusMsg>>,
@@ -200,6 +202,7 @@ impl<P: OnChainConfigProvider> EpochManager<P> {
             author,
             config,
             execution_config,
+            randomness_override_seq_num: node_config.randomness_override_seq_num,
             time_service,
             self_sender,
             network_sender,
@@ -1048,7 +1051,10 @@ impl<P: OnChainConfigProvider> EpochManager<P> {
 
         let onchain_consensus_config: anyhow::Result<OnChainConsensusConfig> = payload.get();
         let onchain_execution_config: anyhow::Result<OnChainExecutionConfig> = payload.get();
-        let onchain_randomness_config: anyhow::Result<RandomnessConfigMoveStruct> = payload.get();
+        let onchain_randomness_config_seq_num: anyhow::Result<RandomnessConfigSeqNum> =
+            payload.get();
+        let randomness_config_move_struct: anyhow::Result<RandomnessConfigMoveStruct> =
+            payload.get();
         let onchain_jwk_consensus_config: anyhow::Result<OnChainJWKConsensusConfig> = payload.get();
         let dkg_state = payload.get::<DKGState>();
 
@@ -1060,7 +1066,7 @@ impl<P: OnChainConfigProvider> EpochManager<P> {
             error!("Failed to read on-chain execution config {}", error);
         }
 
-        if let Err(error) = &onchain_randomness_config {
+        if let Err(error) = &randomness_config_move_struct {
             error!("Failed to read on-chain randomness config {}", error);
         }
 
@@ -1069,9 +1075,25 @@ impl<P: OnChainConfigProvider> EpochManager<P> {
         let consensus_config = onchain_consensus_config.unwrap_or_default();
         let execution_config = onchain_execution_config
             .unwrap_or_else(|_| OnChainExecutionConfig::default_if_missing());
-        let onchain_randomness_config = onchain_randomness_config
-            .and_then(OnChainRandomnessConfig::try_from)
-            .unwrap_or_else(|_| OnChainRandomnessConfig::default_if_missing());
+        let onchain_randomness_config_seq_num = onchain_randomness_config_seq_num
+            .unwrap_or_else(|_| RandomnessConfigSeqNum::default_if_missing());
+
+        info!(
+            epoch = epoch_state.epoch,
+            local = self.randomness_override_seq_num,
+            onchain = onchain_randomness_config_seq_num.seq_num,
+            "Checking randomness config override."
+        );
+        if self.randomness_override_seq_num > onchain_randomness_config_seq_num.seq_num {
+            warn!("Randomness will be force-disabled by local config!");
+        }
+
+        let onchain_randomness_config = OnChainRandomnessConfig::from_configs(
+            self.randomness_override_seq_num,
+            onchain_randomness_config_seq_num.seq_num,
+            randomness_config_move_struct.ok(),
+        );
+
         let jwk_consensus_config = onchain_jwk_consensus_config.unwrap_or_else(|_| {
             // `jwk_consensus_config` not yet initialized, falling back to the old configs.
             Self::equivalent_jwk_consensus_config_from_deprecated_resources(&payload)
```

### consensus/src/rand/rand_gen/rand_manager.rs
```diff
@@ -33,6 +33,7 @@ use aptos_types::{
     validator_signer::ValidatorSigner,
 };
 use bytes::Bytes;
+use fail::fail_point;
 use futures::{
     future::{AbortHandle, Abortable},
     FutureExt, StreamExt,
@@ -170,6 +171,7 @@ impl<S: TShare, D: TAugmentedData> RandManager<S, D> {
             .iter()
             .flat_map(|b| b.ordered_blocks.iter().map(|b3| b3.round()))
             .collect();
+        fail_point!("rand_manager::process_ready_blocks", |_| {});
         info!(rounds = rounds, "Processing rand-ready blocks.");
 
         for blocks in ready_blocks {
```

### crates/aptos/src/test/mod.rs
```diff
@@ -959,6 +959,25 @@ impl CliTestFramework {
         .await
     }
 
+    pub async fn run_script_with_gas_options(
+        &self,
+        index: usize,
+        script_contents: &str,
+        gas_options: Option<GasOptions>,
+    ) -> CliTypedResult<TransactionSummary> {
+        self.run_script_with_framework_package_and_gas_options(
+            index,
+            script_contents,
+            FrameworkPackageArgs {
+                framework_git_rev: None,
+                framework_local_dir: Some(Self::aptos_framework_dir()),
+                skip_fetch_latest_git_deps: false,
+            },
+            gas_options,
+        )
+        .await
+    }
+
     /// Runs the given script contents using the aptos_framework from aptos-core git repository.
     pub async fn run_script_with_default_framework(
         &self,
@@ -979,6 +998,22 @@ impl CliTestFramework {
         index: usize,
         script_contents: &str,
         framework_package_args: FrameworkPackageArgs,
+    ) -> CliTypedResult<TransactionSummary> {
+        self.run_script_with_framework_package_and_gas_options(
+            index,
+            script_contents,
+            framework_package_args,
+            None,
+        )
+        .await
+    }
+
+    pub async fn run_script_with_framework_package_and_gas_options(
+        &self,
+        index: usize,
+        script_contents: &str,
+        framework_package_args: FrameworkPackageArgs,
+        gas_options: Option<GasOptions>,
     ) -> CliTypedResult<TransactionSummary> {
         // Make a temporary directory for compilation
         let temp_dir = TempDir::new().map_err(|err| {
@@ -994,7 +1029,7 @@ impl CliTestFramework {
         .unwrap();
 
         RunScript {
-            txn_options: self.transaction_options(index, None),
+            txn_options: self.transaction_options(index, gas_options),
             compile_proposal_args: CompileScriptFunction {
                 script_path: Some(source_path),
                 compiled_script_path: None,
```
