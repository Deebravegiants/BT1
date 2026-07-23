[File: 'solana/programs/bridge_token_factory/src/error.rs -> Scope: Critical. Irreversible fund lock, frozen redemption path, or permanently unclaimable user or protocol value'] [Function: state/message/mod.rs::SignedPayload::verify_signature] Can an unprivileged attacker exploit the absence of a chain-ID or program-ID domain separator in the signed message serialization to replay a finalize_transfer SignedPayload from one Solana deployment (e.g., mainnet) on another deployment (e.g., devnet or a fork) with the same derived_near_bridge_address, causing double-credit of tokens on the second deployment while the nonce is consumed on the first? Preconditions: serialize_for_near for FinalizeTransferPayload includes SOLANA_OMNI_BRIDGE_CHAIN_ID as a single byte but does not include the Solana program ID or deployment-specific salt; if two deployments share the same derived_near_bridge_address and SOLANA_OMNI_BRIDGE_CHAIN_ID, a signature valid on one is valid on the other. Call sequence: (1) NEAR signs finalize payload for mainnet Solana deployment; (2) relayer finalizes on mainnet — nonce consumed; (3) attacker submits same SignedPayload to devnet deployment with same derived_near_bridge_address; (4) verify_signature passes (same hash, same signer); (5) nonce N not yet used on devnet; (6) tokens minted/transferred on devnet. Invariant tested: signed payloads must be bound to a specific deployment; cross-deployment replay must be cryptographically impossible. Scoped impact: unauthorized token creation on

### Citations

**File:** solana/programs/bridge_token_factory/src/error.rs (L1-27)
```rust
use anchor_lang::prelude::*;

#[error_code(offset = 6000)]
pub enum ErrorCode {
    #[msg(
