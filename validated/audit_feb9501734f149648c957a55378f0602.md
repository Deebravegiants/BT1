### Title
`ConfigManager::set_node_dynamic_config` Lacks Caller Authentication, Allowing Unauthorized Manipulation of Consensus and Gas-Price Parameters — (File: `crates/apollo_config_manager/src/config_manager.rs`)

---

### Summary

The `ConfigManager` component exposes a `SetNodeDynamicConfig` request variant that rewrites the entire live `NodeDynamicConfig` — including consensus gas-price overrides, `compare_retrospective_block_hash`, `stop_at_height`, and gateway admission flags — without verifying the identity of the caller. In a distributed deployment the `ConfigManager` is reachable over a plain TCP socket (`RemoteComponentClient`) with no authentication layer, so any process that can reach that port can silently redirect consensus parameters, corrupt fee accounting, or halt the sequencer.

---

### Finding Description

`ConfigManager::handle_request` dispatches `ConfigManagerRequest::SetNodeDynamicConfig` directly to `set_node_dynamic_config`:

```rust
// crates/apollo_config_manager/src/config_manager.rs  lines 36-42
ConfigManagerRequest::SetNodeDynamicConfig(new_config) => {
    ConfigManagerResponse::SetNodeDynamicConfig(
        $self.set_node_dynamic_config(*new_config).await,
    )
}
```

`set_node_dynamic_config` performs only a structural `validate()` check and then unconditionally overwrites the live config:

```rust
// lines 59-73
pub(crate) async fn set_node_dynamic_config(
    &self,
    node_dynamic_config: NodeDynamicConfig,
) -> ConfigManagerResult<()> {
    if let Err(errors) = node_dynamic_config.validate() { … return Err(…); }
    let mut config = self.latest_node_dynamic_config.write().await;
    *config = node_dynamic_config;
    Ok(())
}
```

There is no check on *who* sent the request. The `ConfigManagerClient` trait exposes `set_node_dynamic_config` to every holder of a `SharedConfigManagerClient`:

```rust
// crates/apollo_config_manager_types/src/communication.rs  lines 61-64
async fn set_node_dynamic_config(
    &self,
    config: NodeDynamicConfig,
) -> ConfigManagerClientResult<()>;
```

In a distributed deployment the `ConfigManager` is served by a `RemoteComponentClient` over TCP. The `apollo_infra` transport layer adds no authentication. Any process that can reach the port — including other sequencer components (consensus, batcher, mempool, HTTP server) that hold a `SharedConfigManagerClient` for read-only `get_*` calls — can also issue `SetNodeDynamicConfig` with an arbitrary payload.

The `NodeDynamicConfig` fields that can be overwritten include:

| Field | Effect |
|---|---|
| `ContextDynamicConfig::override_l2_gas_price_fri` | Forces a fixed L2 gas price into every proposal and validation check |
| `ContextDynamicConfig::override_l1_gas_price_fri / override_l1_data_gas_price_fri` | Overrides L1 gas prices embedded in block headers |
| `ContextDynamicConfig::compare_retrospective_block_hash` | Disables the retrospective block-hash security check in `initiate_validation` |
| `ConsensusDynamicConfig::stop_at_height` | Halts consensus at an arbitrary height |
| `HttpServerDynamicConfig::accept_new_txs` | Closes the gateway to all new transactions |

---

### Impact Explanation

**Gas / fee corruption (Critical):** Setting `override_l2_gas_price_fri` to an attacker-chosen value causes every subsequent proposal built by the node to embed that price in `ProposalInit.l2_gas_price_fri`. Validators that read `ContextDynamicConfig.override_l2_gas_price_fri` during `validate_proposal` will accept proposals whose gas price matches the injected override, producing blocks with wrong fee accounting and incorrect L2 gas prices in block headers — a direct economic impact on every transaction in those blocks.

**Proposal validation bypass (High):** Setting `compare_retrospective_block_hash: false` disables the `retrospective_block_hash` check inside `initiate_validation`, removing a guard that ties each validated block to a known historical anchor.

**Admission disruption (High):** Setting `accept_new_txs: false` in `HttpServerDynamicConfig` causes the HTTP server to reject all incoming transactions, silently halting transaction ingestion without any operator action.

**Consensus halt:** Setting `stop_at_height` to the current block number causes the consensus manager to stop proposing and loop indefinitely.

---

### Likelihood Explanation

In a distributed (Kubernetes) deployment the `ConfigManager` runs as a separate pod. Its TCP port is reachable by any other pod in the same cluster namespace. No Kubernetes `NetworkPolicy` is enforced by default. Any compromised sidecar, misconfigured service, or lateral-movement foothold inside the cluster can issue `SetNodeDynamicConfig` without credentials. In a consolidated single-process deployment the attack surface is smaller (local channels only), but the missing guard is still a latent risk for any future distributed rollout.

---

### Recommendation

1. **Restrict the write path at the transport layer.** Expose `SetNodeDynamicConfig` only on a separate, operator-only port (or Unix socket) that is not shared with the read-only `get_*` endpoints used by consensus, batcher, and mempool components.
2. **Add a caller-identity check inside `set_node_dynamic_config`.** The `ConfigManagerRunner` is the only legitimate caller; a shared secret, mTLS certificate, or a separate `ConfigManagerWriterClient` trait (without `set_node_dynamic_config`) for all other components would enforce this.
3. **Split the trait.** Define a `ConfigManagerReaderClient` (only `get_*` methods) and a `ConfigManagerWriterClient` (adds `set_node_dynamic_config`). Issue only the reader client to consensus, batcher, mempool, and HTTP server components.

---

### Proof of Concept

```
# Distributed deployment: ConfigManager TCP port is reachable at <config-manager-host>:<port>

# 1. Craft a NodeDynamicConfig payload that passes validate() but injects a malicious gas price:
#    override_l2_gas_price_fri = Some(1)   # forces 1 FRI/gas into every proposal
#    compare_retrospective_block_hash = false

# 2. Serialize as ConfigManagerRequest::SetNodeDynamicConfig(payload)
#    (same wire format used by RemoteComponentClient)

# 3. Send to <config-manager-host>:<port> — no credentials required.

# 4. ConfigManager::set_node_dynamic_config() passes validate(), writes the config.

# 5. On the next call to set_height_and_round(), SequencerConsensusContext::update_dynamic_config()
#    fetches the poisoned ContextDynamicConfig via get_context_dynamic_config().

# 6. build_proposal() and validate_proposal() now use override_l2_gas_price_fri = 1,
#    embedding 1 FRI/gas in ProposalInit.l2_gas_price_fri and in every block header,
#    causing incorrect fee accounting for all transactions in subsequent blocks.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** crates/apollo_config_manager/src/config_manager.rs (L36-42)
```rust
            ConfigManagerRequest::SetNodeDynamicConfig(new_config) => {
                ConfigManagerResponse::SetNodeDynamicConfig(
                    $self.set_node_dynamic_config(*new_config).await,
                )
            }
        }
    };
```

**File:** crates/apollo_config_manager/src/config_manager.rs (L59-73)
```rust
    pub(crate) async fn set_node_dynamic_config(
        &self,
        node_dynamic_config: NodeDynamicConfig,
    ) -> ConfigManagerResult<()> {
        info!("ConfigManager: updating node dynamic config");
        if let Err(errors) = node_dynamic_config.validate() {
            error!(
                "ConfigManager: dynamic config update rejected: {errors}. Keeping previous config."
            );
            return Err(ConfigManagerError::InvalidConfig(errors.to_string()));
        }
        let mut config = self.latest_node_dynamic_config.write().await;
        *config = node_dynamic_config;
        Ok(())
    }
```

**File:** crates/apollo_config_manager_types/src/communication.rs (L61-64)
```rust
    async fn set_node_dynamic_config(
        &self,
        config: NodeDynamicConfig,
    ) -> ConfigManagerClientResult<()>;
```

**File:** crates/apollo_config_manager_types/src/communication.rs (L73-83)
```rust
pub enum ConfigManagerRequest {
    GetConsensusDynamicConfig,
    GetClassManagerDynamicConfig,
    GetContextDynamicConfig,
    GetHttpServerDynamicConfig,
    GetMempoolDynamicConfig,
    GetBatcherDynamicConfig,
    GetStateSyncDynamicConfig,
    GetStakingManagerDynamicConfig,
    SetNodeDynamicConfig(Box<NodeDynamicConfig>),
}
```

**File:** crates/apollo_consensus_orchestrator_config/src/config.rs (L267-310)
```rust
pub struct ContextDynamicConfig {
    /// Safety margin in milliseconds to make sure that the batcher completes building the proposal
    /// with enough time for the Fin to be checked by validators.
    #[serde(
        deserialize_with = "deserialize_milliseconds_to_duration",
        serialize_with = "serialize_duration_as_milliseconds"
    )]
    pub build_proposal_margin_millis: Duration,
    /// The minimum L1 gas price in wei.
    pub min_l1_gas_price_wei: u128,
    /// The maximum L1 gas price in wei.
    pub max_l1_gas_price_wei: u128,
    /// The minimum L1 data gas price in wei.
    pub min_l1_data_gas_price_wei: u128,
    /// The maximum L1 data gas price in wei.
    pub max_l1_data_gas_price_wei: u128,
    /// Part per thousand of multiplicative factor to apply to the data gas price, to enable
    /// fine-tuning of the price charged to end users. Commonly used to apply a discount due to
    /// the blob's data being compressed. Can be used to raise the prices in case of blob
    /// under-utilization.
    pub l1_data_gas_price_multiplier_ppt: u128,
    /// This additional gas is added to the L1 gas price.
    pub l1_gas_tip_wei: u128,
    /// SNIP-35 target USD cost per L2 gas unit, in atto-USD ($0.88 per 1e9 L2 gas = 880_000_000
    /// atto-USD).
    pub snip35_target_atto_usd_per_l2_gas: u128,
    /// If given, will override the L2 gas price.
    pub override_l2_gas_price_fri: Option<u128>,
    /// If given, will override the L1 gas price in FRI.
    pub override_l1_gas_price_fri: Option<u128>,
    /// If given, will override the L1 data gas price in FRI.
    pub override_l1_data_gas_price_fri: Option<u128>,
    // TODO(guyn): remove this after we completely remove wei prices from block info.
    /// If given, will override the conversion rate.
    pub override_eth_to_fri_rate: Option<u128>,
    // List of minimum L2 gas prices per block height.
    // Format: "height1:price1,height2:price2,height3:price3"
    #[serde(
        deserialize_with = "deserialize_price_per_height_from_string",
        serialize_with = "serialize_price_per_height_as_string"
    )]
    pub min_l2_gas_price_per_height: Vec<PricePerHeight>,
    pub compare_retrospective_block_hash: bool,
}
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L443-476)
```rust
async fn initiate_validation(
    batcher: Arc<dyn BatcherClient>,
    state_sync_client: SharedStateSyncClient,
    init: &ProposalInit,
    proposal_id: ProposalId,
    timeout_plus_margin: Duration,
    clock: &dyn Clock,
    compare_retrospective_block_hash: bool,
) -> ValidateProposalResult<()> {
    let chrono_timeout = chrono::Duration::from_std(timeout_plus_margin)
        .expect("Can't convert timeout to chrono::Duration");

    let input = ValidateBlockInput {
        proposal_id,
        deadline: clock.now() + chrono_timeout,
        retrospective_block_hash: retrospective_block_hash(
            batcher.clone(),
            state_sync_client,
            init,
            compare_retrospective_block_hash,
        )
        .await
        .map_err(ValidateProposalError::from)?,
        block_info: convert_to_sn_api_block_info(init)?,
    };
    debug!("Initiating validate proposal: input={input:?}");
    batcher.validate_block(input.clone()).await.map_err(|err| {
        ValidateProposalError::Batcher(
            format!("Failed to initiate validate proposal {input:?}."),
            err,
        )
    })?;
    Ok(())
}
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1274-1289)
```rust
    async fn update_dynamic_config(&mut self) {
        if let Some(config_manager_client) = self.deps.config_manager_client.clone() {
            let config_result = config_manager_client.get_context_dynamic_config().await;
            match config_result {
                Ok(config) => {
                    self.config.dynamic_config = config;
                }
                Err(e) => {
                    error!(
                        "Failed to get dynamic config for consensus context. Config not updated. \
                         Error: {e:?}"
                    );
                }
            }
        }
    }
```
