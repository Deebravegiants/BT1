No vulnerability found for this question.

**Reasoning:** `RandomnessConfigSeqNum::from_configs` in `types/src/on_chain_config/randomness_config.rs` compares a node's compiled-in `local_seqnum` against the on-chain `onchain_seqnum` to decide whether to fall back to `default_disabled()` during a binary upgrade rollout [1](#0-0) . The `local_seqnum` value is a hardcoded constant tied to the validator's software version, not data derived from any unprivileged transaction, package, view, API, bytecode, or proof input — it is read internally by `DKGManager`/`EpochManager` when constructing on-chain config from `OnChainConfigPayload` at epoch boundaries [2](#0-1) . This mechanism is an intentional, documented safety gate for coordinating validator binary upgrades (an un-upgraded node deliberately disables randomness rather than risk misinterpreting a newer on-chain config schema), and any transient divergence it could cause is confined to which nodes participate in DKG/randomness for an epoch — it does not touch object ownership, fungible asset balances, freeze/mint/burn authority, multisig or resource-account control, or any other custody-grade state. Since there is no unprivileged-input path crossing a custody boundary and no asset/ownership impact, this does not meet the review's decision standard or required impacts.

### Citations

**File:** types/src/on_chain_config/randomness_config.rs (L128-140)
```rust
    pub fn from_configs(
        local_seqnum: u64,
        onchain_seqnum: u64,
        onchain_raw_config: Option<RandomnessConfigMoveStruct>,
    ) -> Self {
        if local_seqnum > onchain_seqnum {
            Self::default_disabled()
        } else {
            onchain_raw_config
                .and_then(|onchain_raw| OnChainRandomnessConfig::try_from(onchain_raw).ok())
                .unwrap_or_else(OnChainRandomnessConfig::default_if_missing)
        }
    }
```

**File:** dkg/src/epoch_manager.rs (L25-36)
```rust
use aptos_types::{
    account_address::AccountAddress,
    dkg::{
        chunky_dkg::{ChunkyDKGStartEvent, ChunkyDKGState},
        DKGStartEvent, DKGState, DefaultDKG,
    },
    epoch_state::EpochState,
    on_chain_config::{
        ChunkyDKGConfigMoveStruct, ChunkyDKGConfigSeqNum, OnChainChunkyDKGConfig,
        OnChainConfigPayload, OnChainConfigProvider, OnChainConsensusConfig,
        OnChainRandomnessConfig, RandomnessConfigMoveStruct, RandomnessConfigSeqNum, ValidatorSet,
    },
```
