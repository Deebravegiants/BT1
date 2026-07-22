### Title
Missing `get_gateway_dynamic_config` Getter Causes Gateway's `native_classes_whitelist` to Be Permanently Frozen at Startup — (`File: crates/apollo_config_manager/src/config_manager.rs`, `crates/apollo_config_manager_types/src/communication.rs`)

---

### Summary

`NodeDynamicConfig` stores a `gateway_dynamic_config: Option<GatewayDynamicConfig>` field alongside eight other per-component dynamic configs. Every other field has a corresponding getter in `ConfigManager` and a matching variant in `ConfigManagerRequest`/`ConfigManagerResponse`/`ConfigManagerClient`. `gateway_dynamic_config` has none. The `ConfigManagerRunner` periodically calls `set_node_dynamic_config` (which writes the updated `gateway_dynamic_config` into the shared `RwLock`), but the gateway component can never call a getter to retrieve the new value. The gateway's `native_classes_whitelist` is therefore permanently frozen at the value it had at node startup, silently diverging from the batcher's whitelist after any live config update.

---

### Finding Description

`NodeDynamicConfig` declares nine optional sub-configs:

```
batcher_dynamic_config, class_manager_dynamic_config, consensus_dynamic_config,
context_dynamic_config, gateway_dynamic_config,          ← no getter
http_server_dynamic_config, mempool_dynamic_config,
staking_manager_dynamic_config, state_sync_dynamic_config
```

`ConfigManager` exposes getters for all of them **except** `gateway_dynamic_config`:

```rust
// crates/apollo_config_manager/src/config_manager.rs  lines 75-129
pub(crate) async fn get_consensus_dynamic_config(...)
pub(crate) async fn get_class_manager_dynamic_config(...)
pub(crate) async fn get_context_dynamic_config(...)
pub(crate) async fn get_http_server_dynamic_config(...)
pub(crate) async fn get_mempool_dynamic_config(...)
pub(crate) async fn get_batcher_dynamic_config(...)
pub(crate) async fn get_state_sync_dynamic_config(...)
pub(crate) async fn get_staking_manager_dynamic_config(...)
// get_gateway_dynamic_config  ← MISSING
```

The `ConfigManagerClient` trait and the `ConfigManagerRequest`/`ConfigManagerResponse` enums mirror this omission:

```rust
// crates/apollo_config_manager_types/src/communication.rs  lines 38-65, 73-83, 96-106
pub enum ConfigManagerRequest {
    GetConsensusDynamicConfig, GetClassManagerDynamicConfig, GetContextDynamicConfig,
    GetHttpServerDynamicConfig, GetMempoolDynamicConfig, GetBatcherDynamicConfig,
    GetStateSyncDynamicConfig, GetStakingManagerDynamicConfig,
    SetNodeDynamicConfig(Box<NodeDynamicConfig>),
    // GetGatewayDynamicConfig  ← MISSING
}
```

`GatewayDynamicConfig` contains exactly one field:

```rust
// crates/apollo_gateway_config/src/config.rs  lines 149-152
pub struct GatewayDynamicConfig {
    pub native_classes_whitelist: NativeClassesWhitelist,
}
```

`NativeClassesWhitelist` is the runtime switch that decides whether a contract class is executed as Cairo native or CASM:

```rust
// crates/blockifier/src/blockifier/config.rs  lines 188-192
pub enum NativeClassesWhitelist {
    All,
    Limited(Vec<ClassHash>),
}
```

The gateway's stateful validator factory reads this whitelist at validation time:

```rust
// crates/apollo_gateway/src/stateful_transaction_validator.rs  lines 86-119
async fn instantiate_validator(
    &self,
    native_classes_whitelist: NativeClassesWhitelist,
) -> ...
```

The batcher's block builder also reads it, but via `get_batcher_dynamic_config()` — a live call to the config manager that returns the current value. The gateway has no equivalent call path; it is initialized once with `gateway_config.clone()` and never refreshed.

---

### Impact Explanation

`NativeClassesWhitelist` selects which compiled artifact (native vs CASM) is loaded for a given class hash during execution. After a live config update that changes the whitelist (e.g., operator restricts native execution to a specific set of class hashes to mitigate a native-compilation bug), the batcher picks up the new whitelist via `get_batcher_dynamic_config()`, but the gateway continues using the stale `All` whitelist. The two components now disagree on which compiled class to use for the same class hash. This maps directly to the allowed impact: **wrong compiled class / CASM/native artifact selected for execution** (Critical), and **gateway admission uses a different execution path than the sequencer** (High).

---

### Likelihood Explanation

The `ConfigManagerRunner` is designed to watch the config file and push updates automatically. Any operator who updates `native_classes_whitelist` in the config file (a routine operational action) will silently produce a gateway/batcher split. The gateway gives no error; it simply continues using the stale whitelist indefinitely.

---

### Recommendation

Add the missing getter symmetrically with all other dynamic config fields:

1. **`crates/apollo_config_manager/src/config_manager.rs`** — add:
```rust
pub(crate) async fn get_gateway_dynamic_config(
    &self,
) -> ConfigManagerResult<GatewayDynamicConfig> {
    let config = self.latest_node_dynamic_config.read().await;
    Ok(config.gateway_dynamic_config.as_ref().unwrap().clone())
}
```
and add `(GetGatewayDynamicConfig, get_gateway_dynamic_config)` to the `handle_config_request!` macro invocation.

2. **`crates/apollo_config_manager_types/src/communication.rs`** — add `GetGatewayDynamicConfig` to `ConfigManagerRequest`, `ConfigManagerResponse`, and `ConfigManagerClient`.

3. **`crates/apollo_gateway/src/gateway.rs`** — make the gateway call `config_manager_client.get_gateway_dynamic_config()` per transaction (or per block) instead of reading from the frozen startup config.

---

### Proof of Concept

1. Start the node with `gateway_config.dynamic_config.native_classes_whitelist = "All"`.
2. Deploy a Cairo 1 contract (class hash `0xABCD`).
3. Update the config file to set `native_classes_whitelist = '["0xABCD"]'` (restrict to one class).
4. The `ConfigManagerRunner` detects the change and calls `set_node_dynamic_config`; the new `gateway_dynamic_config` is stored in the `RwLock`.
5. Submit a transaction that invokes a **different** class hash (not `0xABCD`).
6. The batcher calls `get_batcher_dynamic_config()`, receives `Limited(["0xABCD"])`, and executes the class as CASM.
7. The gateway calls `instantiate_validator` with the stale `All` whitelist (from startup), and executes the same class as native.
8. If native and CASM produce divergent results for this class (e.g., due to a native compilation bug), the gateway's validation outcome differs from the batcher's execution outcome — the gateway admits a transaction whose on-chain execution will produce a different result than the gateway predicted. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** crates/apollo_node_config/src/node_config.rs (L358-379)
```rust
#[derive(Debug, Deserialize, Serialize, Clone, PartialEq, Validate, Default)]
#[validate(schema(function = "validate_node_dynamic_config"))]
pub struct NodeDynamicConfig {
    #[validate(nested)]
    pub batcher_dynamic_config: Option<BatcherDynamicConfig>,
    #[validate(nested)]
    pub class_manager_dynamic_config: Option<ClassManagerDynamicConfig>,
    #[validate(nested)]
    pub consensus_dynamic_config: Option<ConsensusDynamicConfig>,
    #[validate(nested)]
    pub context_dynamic_config: Option<ContextDynamicConfig>,
    #[validate(nested)]
    pub gateway_dynamic_config: Option<GatewayDynamicConfig>,
    #[validate(nested)]
    pub http_server_dynamic_config: Option<HttpServerDynamicConfig>,
    #[validate(nested)]
    pub mempool_dynamic_config: Option<MempoolDynamicConfig>,
    #[validate(nested)]
    pub staking_manager_dynamic_config: Option<StakingManagerDynamicConfig>,
    #[validate(nested)]
    pub state_sync_dynamic_config: Option<StateSyncDynamicConfig>,
}
```

**File:** crates/apollo_config_manager/src/config_manager.rs (L75-130)
```rust
    pub(crate) async fn get_consensus_dynamic_config(
        &self,
    ) -> ConfigManagerResult<ConsensusDynamicConfig> {
        let config = self.latest_node_dynamic_config.read().await;
        Ok(config.consensus_dynamic_config.as_ref().unwrap().clone())
    }

    pub(crate) async fn get_class_manager_dynamic_config(
        &self,
    ) -> ConfigManagerResult<ClassManagerDynamicConfig> {
        let config = self.latest_node_dynamic_config.read().await;
        Ok(config.class_manager_dynamic_config.as_ref().unwrap().clone())
    }

    pub(crate) async fn get_context_dynamic_config(
        &self,
    ) -> ConfigManagerResult<ContextDynamicConfig> {
        let config = self.latest_node_dynamic_config.read().await;
        Ok(config.context_dynamic_config.as_ref().unwrap().clone())
    }

    pub(crate) async fn get_http_server_dynamic_config(
        &self,
    ) -> ConfigManagerResult<HttpServerDynamicConfig> {
        let config = self.latest_node_dynamic_config.read().await;
        Ok(config.http_server_dynamic_config.as_ref().unwrap().clone())
    }

    pub(crate) async fn get_mempool_dynamic_config(
        &self,
    ) -> ConfigManagerResult<MempoolDynamicConfig> {
        let config = self.latest_node_dynamic_config.read().await;
        Ok(config.mempool_dynamic_config.as_ref().unwrap().clone())
    }

    pub(crate) async fn get_batcher_dynamic_config(
        &self,
    ) -> ConfigManagerResult<BatcherDynamicConfig> {
        let config = self.latest_node_dynamic_config.read().await;
        Ok(config.batcher_dynamic_config.as_ref().unwrap().clone())
    }

    pub(crate) async fn get_state_sync_dynamic_config(
        &self,
    ) -> ConfigManagerResult<StateSyncDynamicConfig> {
        let config = self.latest_node_dynamic_config.read().await;
        Ok(config.state_sync_dynamic_config.as_ref().unwrap().clone())
    }

    pub(crate) async fn get_staking_manager_dynamic_config(
        &self,
    ) -> ConfigManagerResult<StakingManagerDynamicConfig> {
        let config = self.latest_node_dynamic_config.read().await;
        Ok(config.staking_manager_dynamic_config.as_ref().unwrap().clone())
    }
}
```

**File:** crates/apollo_config_manager/src/config_manager.rs (L132-150)
```rust
#[async_trait]
impl ComponentRequestHandler<ConfigManagerRequest, ConfigManagerResponse> for ConfigManager {
    async fn handle_request(&mut self, request: ConfigManagerRequest) -> ConfigManagerResponse {
        // Note: the `ConfigManagerRequest::SetNodeDynamicConfig` variant is handled inside the
        // macro.
        handle_config_request!(
            self,
            request,
            (GetBatcherDynamicConfig, get_batcher_dynamic_config),
            (GetClassManagerDynamicConfig, get_class_manager_dynamic_config),
            (GetConsensusDynamicConfig, get_consensus_dynamic_config),
            (GetContextDynamicConfig, get_context_dynamic_config),
            (GetHttpServerDynamicConfig, get_http_server_dynamic_config),
            (GetMempoolDynamicConfig, get_mempool_dynamic_config),
            (GetStakingManagerDynamicConfig, get_staking_manager_dynamic_config),
            (GetStateSyncDynamicConfig, get_state_sync_dynamic_config),
        )
    }
}
```

**File:** crates/apollo_config_manager_types/src/communication.rs (L38-65)
```rust
pub trait ConfigManagerClient: Send + Sync {
    async fn get_consensus_dynamic_config(
        &self,
    ) -> ConfigManagerClientResult<ConsensusDynamicConfig>;

    async fn get_class_manager_dynamic_config(
        &self,
    ) -> ConfigManagerClientResult<ClassManagerDynamicConfig>;

    async fn get_context_dynamic_config(&self) -> ConfigManagerClientResult<ContextDynamicConfig>;
    async fn get_http_server_dynamic_config(
        &self,
    ) -> ConfigManagerClientResult<HttpServerDynamicConfig>;

    async fn get_mempool_dynamic_config(&self) -> ConfigManagerClientResult<MempoolDynamicConfig>;
    async fn get_batcher_dynamic_config(&self) -> ConfigManagerClientResult<BatcherDynamicConfig>;
    async fn get_state_sync_dynamic_config(
        &self,
    ) -> ConfigManagerClientResult<StateSyncDynamicConfig>;
    async fn get_staking_manager_dynamic_config(
        &self,
    ) -> ConfigManagerClientResult<StakingManagerDynamicConfig>;

    async fn set_node_dynamic_config(
        &self,
        config: NodeDynamicConfig,
    ) -> ConfigManagerClientResult<()>;
}
```

**File:** crates/apollo_config_manager_types/src/communication.rs (L73-106)
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
impl_debug_for_infra_requests_and_responses!(ConfigManagerRequest);
impl_labeled_request!(ConfigManagerRequest, ConfigManagerRequestLabelValue);
impl PrioritizedRequest for ConfigManagerRequest {}

const CONFIG_MANAGER_REQUEST_TYPE_LABEL: &str = "request_type";

generate_permutation_labels! {
    CONFIG_MANAGER_REQUEST_LABELS,
    (CONFIG_MANAGER_REQUEST_TYPE_LABEL, ConfigManagerRequestLabelValue),
}

#[derive(Clone, Serialize, Deserialize, AsRefStr)]
pub enum ConfigManagerResponse {
    GetConsensusDynamicConfig(ConfigManagerResult<ConsensusDynamicConfig>),
    GetClassManagerDynamicConfig(ConfigManagerResult<ClassManagerDynamicConfig>),
    GetContextDynamicConfig(ConfigManagerResult<ContextDynamicConfig>),
    GetHttpServerDynamicConfig(ConfigManagerResult<HttpServerDynamicConfig>),
    GetMempoolDynamicConfig(ConfigManagerResult<MempoolDynamicConfig>),
    GetBatcherDynamicConfig(ConfigManagerResult<BatcherDynamicConfig>),
    GetStateSyncDynamicConfig(ConfigManagerResult<StateSyncDynamicConfig>),
    GetStakingManagerDynamicConfig(ConfigManagerResult<StakingManagerDynamicConfig>),
    SetNodeDynamicConfig(ConfigManagerResult<()>),
}
```

**File:** crates/apollo_gateway_config/src/config.rs (L149-164)
```rust
#[derive(Clone, Debug, Deserialize, PartialEq, Serialize, Validate)]
pub struct GatewayDynamicConfig {
    pub native_classes_whitelist: NativeClassesWhitelist,
}

impl Default for GatewayDynamicConfig {
    fn default() -> Self {
        Self { native_classes_whitelist: NativeClassesWhitelist::All }
    }
}

impl SerializeConfig for GatewayDynamicConfig {
    fn dump(&self) -> BTreeMap<ParamPath, SerializedParam> {
        BTreeMap::from_iter([self.native_classes_whitelist.ser_param()])
    }
}
```

**File:** crates/blockifier/src/blockifier/config.rs (L188-254)
```rust
#[derive(Clone, Debug, PartialEq)]
pub enum NativeClassesWhitelist {
    All,
    Limited(Vec<ClassHash>),
}

impl NativeClassesWhitelist {
    pub const SER_PARAM_DESCRIPTION: &str = "Specifies whether to execute all class hashes or \
                                             only specific ones using Cairo native. If limited, a \
                                             specific list of class hashes is provided.";

    pub fn ser_param(&self) -> (String, SerializedParam) {
        ser_param(
            "native_classes_whitelist",
            &self,
            Self::SER_PARAM_DESCRIPTION,
            ParamPrivacyInput::Public,
        )
    }
}

impl<'de> Deserialize<'de> for NativeClassesWhitelist {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let raw: String = <String as serde::Deserialize>::deserialize(deserializer)?;

        if raw == "All" {
            return Ok(NativeClassesWhitelist::All);
        }
        // Support stringified JSON array: "[\"0x..\", \"0x..\"]"
        match serde_json::from_str::<Vec<ClassHash>>(&raw) {
            Ok(vec) => Ok(NativeClassesWhitelist::Limited(vec)),
            Err(_) => Err(de::Error::custom(format!(
                "invalid native_classes_whitelist string: expected \"All\" or stringified JSON \
                 array, (i.e., \"[\\\"0x..\\\", \\\"0x..\\\"]\") got: {}",
                raw
            ))),
        }
    }
}

impl Serialize for NativeClassesWhitelist {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        match self {
            NativeClassesWhitelist::All => serializer.serialize_str("All"),
            NativeClassesWhitelist::Limited(vec) => {
                let json = serde_json::to_string(vec)
                    .expect("Failed to stringify whitelist to JSON array");
                serializer.serialize_str(&json)
            }
        }
    }
}

impl NativeClassesWhitelist {
    pub fn contains(&self, class_hash: &ClassHash) -> bool {
        match self {
            NativeClassesWhitelist::All => true,
            NativeClassesWhitelist::Limited(contracts) => contracts.contains(class_hash),
        }
    }
}
```

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L86-119)
```rust
    async fn instantiate_validator(
        &self,
        native_classes_whitelist: NativeClassesWhitelist,
    ) -> StatefulTransactionValidatorResult<Box<Self::Validator>> {
        // TODO(yael 6/5/2024): consider storing the block_info as part of the
        // StatefulTransactionValidator and update it only once a new block is created.
        let (blockifier_state_reader, gateway_fixed_block_state_reader) = self
            .state_reader_factory
            .get_blockifier_state_reader_and_gateway_fixed_block_from_latest_block()
            .await
            .map_err(|err| GatewaySpecError::UnexpectedError {
                data: format!("Internal server error: {err}"),
            })
            .map_err(|e| {
                StarknetError::internal_with_logging(
                    "Failed to get state reader from latest block",
                    e,
                )
            })?;
        let state_reader_and_contract_manager =
            StateReaderAndContractManager::new_with_native_classes_whitelist(
                blockifier_state_reader,
                self.contract_class_manager.clone(),
                native_classes_whitelist,
                Some(GATEWAY_CLASS_CACHE_METRICS),
            );

        Ok(Box::new(StatefulTransactionValidator::new(
            self.config.clone(),
            self.chain_info.clone(),
            state_reader_and_contract_manager,
            gateway_fixed_block_state_reader,
        )))
    }
```
