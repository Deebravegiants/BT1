No vulnerability found for this question.

**Reasoning:**

Every friend module that calls `config_buffer::upsert` (`consensus_config`, `execution_config`, `epoch_timeout_config`, `jwk_consensus_config`, `randomness_api_v0_config`, `jwks`, `gas_schedule`, `keyless_account`, `version`, `chunky_dkg_config*`, `randomness_config*`, `decryption`) gates its `set_for_next_epoch`/upsert-triggering entry point with `system_addresses::assert_aptos_framework(account)`, requiring the caller to already hold the `@aptos_framework` signer (a privileged, governance-only capability), e.g. [1](#0-0)  and [2](#0-1) . There is no unprivileged path that reaches `config_buffer::upsert` — `upsert` itself is `public(friend)`, restricted to the enumerated framework modules, and can't be called by an arbitrary attacker module at all [3](#0-2) [4](#0-3) .

Additionally, none of the config types buffered via this module (`ConsensusConfig`, `ExecutionConfig`, `EpochTimeoutConfig`, `JWKConsensusConfig`, `RequiredGasDeposit`/`AllowCustomMaxGasFlag`, `SupportedOIDCProviders`, gas schedule, keyless account config, version) contain an address field representing a resource-account or code-object owner that gets applied as a custody authority on `on_new_epoch()` — they hold raw config bytes, booleans, options, or provider lists, e.g. [5](#0-4)  and [6](#0-5) . The `on_new_epoch()` consumers simply overwrite the config resource under `@aptos_framework`; none redirect ownership/authority over a resource account or code object, e.g. [7](#0-6) .

Since (1) reaching `upsert` requires a pre-existing privileged `@aptos_framework` signer, not unprivileged input, and (2) no buffered config type carries an attacker-influenceable address that later grants custody authority, this scenario does not cross a real custody boundary and falls outside the review bounds (requires pre-existing permissions).

### Citations

**File:** aptos-move/framework/aptos-framework/sources/configs/consensus_config.move (L51-55)
```text
    public fun set_for_next_epoch(account: &signer, config: vector<u8>) {
        system_addresses::assert_aptos_framework(account);
        assert!(config.length() > 0, error::invalid_argument(EINVALID_CONFIG));
        std::config_buffer::upsert<ConsensusConfig>(ConsensusConfig {config});
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/epoch_timeout_config.move (L35-38)
```text
    public fun set_for_next_epoch(framework: &signer, new_config: EpochTimeoutConfig) {
        system_addresses::assert_aptos_framework(framework);
        config_buffer::upsert(new_config);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/config_buffer.move (L22-35)
```text
    friend aptos_framework::chunky_dkg_config;
    friend aptos_framework::chunky_dkg_config_seqnum;
    friend aptos_framework::consensus_config;
    friend aptos_framework::decryption;
    friend aptos_framework::epoch_timeout_config;
    friend aptos_framework::execution_config;
    friend aptos_framework::gas_schedule;
    friend aptos_framework::jwks;
    friend aptos_framework::jwk_consensus_config;
    friend aptos_framework::keyless_account;
    friend aptos_framework::randomness_api_v0_config;
    friend aptos_framework::randomness_config;
    friend aptos_framework::randomness_config_seqnum;
    friend aptos_framework::version;
```

**File:** aptos-move/framework/aptos-framework/sources/configs/config_buffer.move (L69-74)
```text
    public(friend) fun upsert<T: drop + store>(config: T) acquires PendingConfigs {
        let configs = borrow_global_mut<PendingConfigs>(@aptos_framework);
        let key = type_info::type_name<T>();
        let value = any::pack(config);
        configs.configs.upsert(key, value);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/execution_config.move (L13-15)
```text
    struct ExecutionConfig has drop, key, store {
        config: vector<u8>,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/execution_config.move (L54-64)
```text
    public(friend) fun on_new_epoch(framework: &signer) acquires ExecutionConfig {
        system_addresses::assert_aptos_framework(framework);
        if (config_buffer::does_exist<ExecutionConfig>()) {
            let config = config_buffer::extract_v2<ExecutionConfig>();
            if (exists<ExecutionConfig>(@aptos_framework)) {
                *borrow_global_mut<ExecutionConfig>(@aptos_framework) = config;
            } else {
                move_to(framework, config);
            };
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/randomness_api_v0_config.move (L8-15)
```text
    struct RequiredGasDeposit has key, drop, store {
        gas_amount: Option<u64>,
    }

    /// If this flag is set, `max_gas` specified inside `#[randomness()]` will be used as the required deposit.
    struct AllowCustomMaxGasFlag has key, drop, store {
        value: bool,
    }
```
