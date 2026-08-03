No vulnerability found for this question.

**Rationale:** `OnChainChunkyDKGConfig::new_v1` in [1](#0-0)  is a Rust-side helper used only by trusted, off-chain tooling (genesis config generation, release-builder proposals, CLI, and test code) to construct a `ChunkyDKGConfigMoveStruct` payload — it is not an entrypoint reachable from an unprivileged transaction, script, or Move function call.

The actual on-chain Move module `chunky_dkg_config::new_v1` takes already-constructed `FixedPoint64` values directly, not raw percentages, so no percentage-to-fraction division happens on-chain: [2](#0-1) . The only ways to install a new `ChunkyDKGConfig` on-chain are `initialize` (framework-signer-gated) and `set_for_next_epoch` (also framework-signer-gated via `system_addresses::assert_aptos_framework`) followed by `on_new_epoch`: [3](#0-2) .

Since the Rust `new_v1` percentage-division logic is only invoked by whoever assembles genesis or governance-approved release proposals (already privileged), and the on-chain Move entrypoint that actually mutates custody-relevant state requires the framework signer, there is no unprivileged path (transaction, package, view, authenticator, API, or bytecode) that reaches this arithmetic. Even granting the numeric claim (dividing `u64::MAX` by 100 in `U64F64` does not overflow since `U64F64` has a 64-bit integer part, it would simply produce an out-of-range threshold value, not a panic), this cannot be triggered by an attacker without pre-existing governance/framework privileges, so it fails the review's custody-boundary requirement.

### Citations

**File:** types/src/on_chain_config/chunky_dkg_config.rs (L69-83)
```rust
    pub fn new_v1(
        secrecy_threshold_in_percentage: u64,
        reconstruct_threshold_in_percentage: u64,
    ) -> Self {
        let secrecy_threshold = FixedPoint64MoveStruct::from_u64f64(
            U64F64::from_num(secrecy_threshold_in_percentage) / U64F64::from_num(100),
        );
        let reconstruction_threshold = FixedPoint64MoveStruct::from_u64f64(
            U64F64::from_num(reconstruct_threshold_in_percentage) / U64F64::from_num(100),
        );
        Self::V1(ConfigV1 {
            secrecy_threshold,
            reconstruction_threshold,
        })
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/chunky_dkg_config.move (L42-69)
```text
    /// Initialize the configuration. Used in genesis or governance.
    public fun initialize(framework: &signer, config: ChunkyDKGConfig) {
        system_addresses::assert_aptos_framework(framework);
        if (!exists<ChunkyDKGConfig>(@aptos_framework)) {
            move_to(framework, config)
        }
    }

    /// This can be called by on-chain governance to update on-chain consensus configs for the next epoch.
    public fun set_for_next_epoch(
        framework: &signer, new_config: ChunkyDKGConfig
    ) {
        system_addresses::assert_aptos_framework(framework);
        config_buffer::upsert(new_config);
    }

    /// Only used in reconfigurations to apply the pending `ChunkyDKGConfig`, if there is any.
    public(friend) fun on_new_epoch(framework: &signer) acquires ChunkyDKGConfig {
        system_addresses::assert_aptos_framework(framework);
        if (config_buffer::does_exist<ChunkyDKGConfig>()) {
            let new_config = config_buffer::extract_v2<ChunkyDKGConfig>();
            if (exists<ChunkyDKGConfig>(@aptos_framework)) {
                *borrow_global_mut<ChunkyDKGConfig>(@aptos_framework) = new_config;
            } else {
                move_to(framework, new_config);
            }
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/chunky_dkg_config.move (L90-99)
```text
    /// Create a `ConfigV1` variant.
    public fun new_v1(
        secrecy_threshold: FixedPoint64, reconstruction_threshold: FixedPoint64
    ): ChunkyDKGConfig {
        ChunkyDKGConfig {
            variant: copyable_any::pack(
                ConfigV1 { secrecy_threshold, reconstruction_threshold }
            )
        }
    }
```
