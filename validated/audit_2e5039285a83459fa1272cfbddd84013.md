## Analog Found

### Title
Hard-fork transaction replay across NEAR networks via hardcoded EVM `CHAIN_ID` in the ETH Wallet Contract - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs`)

### Summary
NEAR's ETH Wallet Contract (used for ETH-implicit accounts to accept RLP-encoded Ethereum-style transactions via `rlp_execute`) validates the `chain_id` field of the incoming Ethereum transaction against a compile-time constant `CHAIN_ID` baked into the WASM at build time, rather than deriving it dynamically from a live, fork-resistant chain identifier. This mirrors the Golom `EIP712_DOMAIN_TYPEHASH` bug class: a signing-domain identifier meant to bind a signature to one specific chain instance is fixed once and never revalidated against the actual running chain, so a hard fork that produces two chains sharing the same network label (and hence the same baked `CHAIN_ID`) allows a single signed authorization to be validly replayed on both resulting chains.

### Finding Description
`CHAIN_ID` is generated at build time by `runtime/near-wallet-contract/build.rs`, which hardcodes `397` for mainnet, `398` for testnet, and `399` for localnet [1](#0-0) , and is embedded into the wallet-contract crate via `std::include!("CHAIN_ID")` [2](#0-1) .

This value is used as the sole chain-binding check for user-signed Ethereum-style transactions submitted through the wallet contract's relayer flow:

```
if tx.chain_id != Some(CHAIN_ID) {
    return Err(Error::Relayer(RelayerError::InvalidChainId));
}
``` [3](#0-2) 

The compiled contract binaries are statically embedded per network label (`MAINNET`, `TESTNET`, `LOCALNET`) in `near-wallet-contract/src/lib.rs` and selected purely by the string chain_id (`"mainnet"`, `"testnet"`, etc.) from genesis config, not by any fork-specific/genesis-hash-derived identifier: [4](#0-3)  and [5](#0-4) .

If NEAR ever undergoes a hard fork that results in two independently operating networks both still identifying with the same `chain_id` label (e.g. `"mainnet"`), both resulting chains would deploy/embed the byte-identical wallet contract WASM with the same hardcoded EVM `CHAIN_ID = 397`. Because ETH-implicit account state (including nonces) is duplicated across both post-fork chains at the moment of the split, a single Ethereum-style transaction signed by a user (with a matching nonce and the shared `CHAIN_ID`) would independently validate and execute on both chains — exactly the "hard fork chainId replay" class described in the Golom report, where a domain separator derived once from `chainid()` fails to distinguish between two chains that share a chain identifier after a split.

### Impact Explanation
A successfully replayed transaction would let a single user-authorized action (transfer, contract call, or key management action via the wallet contract's `Action` set) execute independently on both post-fork chains from one signature, producing an unintended duplicated balance/state change relative to what the user authorized once. This falls into "unauthorized state or balance change" territory for ETH-implicit accounts on NEAR, since the `nonce`/`chain_id` check that is supposed to be the sole replay defense in `validate_tx_relayer_data` no longer differentiates fork instances. This is a narrow-scope EVM-emulation-layer replay condition; it depends on a hard fork occurring and on the two forks retaining the same NEAR chain-id label, matching the same "requires an external hard-fork event" caveat noted for the original Golom finding.

### Likelihood Explanation
Low-to-Medium: it requires an actual NEAR hard fork producing two live chains sharing a chain_id label, which is an infrequent, high-visibility event (similar reasoning as the C4 judge's medium-severity rating for the original Golom finding, which also depended on the external event of a hard fork). The reachable path (relayer-submitted `rlp_execute` calls for ETH-implicit accounts) is fully permissionless and unprivileged, so no special access is needed once the fork exists.

### Recommendation
Bind the wallet contract's transaction validation to a chain-instance identifier that is guaranteed to diverge across a hard fork (e.g., derive it from the genesis hash or another fork-unique protocol value) rather than a static build-time constant tied only to the network name, and/or make the wallet contract able to read/validate against a live, protocol-supplied chain identifier instead of a value frozen into the WASM at compile time.

### Proof of Concept
1. NEAR mainnet undergoes a contentious hard fork, producing chain A and chain B, both still reporting `genesis.config.chain_id == "mainnet"`.
2. Both chains embed/allow the identical wallet-contract WASM (`wallet_contract_mainnet.wasm`) with the same baked `CHAIN_ID = 397` (`runtime/near-wallet-contract/build.rs`).
3. Alice's ETH-implicit account exists with identical state (balance, nonce) on both A and B at fork time.
4. Alice signs one Ethereum-style transaction (nonce `n`, `chain_id: 397`) intending to execute it only on chain A via a relayer's `rlp_execute` call.
5. `validate_tx_relayer_data` on chain B independently validates the same transaction because `tx.chain_id == Some(397)` matches its own baked constant and the nonce still matches Alice's duplicated pre-fork state, so the identical action (e.g., a transfer) executes on chain B as well — a replay the user did not authorize twice.

### Citations

**File:** runtime/near-wallet-contract/build.rs (L9-43)
```rust
/// See https://chainlist.org/chain/397
const MAINNET_CHAIN_ID: u64 = 397;

/// See https://chainlist.org/chain/398
const TESTNET_CHAIN_ID: u64 = 398;

/// Not officially registered on chainlist.org because this is for local testing only.
const LOCALNET_CHAIN_ID: u64 = 399;

fn main() -> anyhow::Result<()> {
    let contract_dir = "./implementation";

    build_contract(
        contract_dir,
        "eth_wallet_contract",
        "wallet_contract_mainnet",
        MAINNET_CHAIN_ID,
    )
    .context("Mainnet build failed")?;

    build_contract(
        contract_dir,
        "eth_wallet_contract",
        "wallet_contract_testnet",
        TESTNET_CHAIN_ID,
    )
    .context("Testnet build failed")?;

    build_contract(
        contract_dir,
        "eth_wallet_contract",
        "wallet_contract_localnet",
        LOCALNET_CHAIN_ID,
    )
    .context("Localnet build failed")?;
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs (L16-20)
```rust
/// The chain ID is pulled from a file to allow this contract to be easily
/// compiled with the appropriate value for the network it will be deployed on.
/// The chain ID for Near mainnet is [397](https://chainlist.org/chain/397)
/// while the value for testnet is [398](https://chainlist.org/chain/398).
pub const CHAIN_ID: u64 = std::include!("CHAIN_ID");
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs (L328-330)
```rust
    if tx.chain_id != Some(CHAIN_ID) {
        return Err(Error::Relayer(RelayerError::InvalidChainId));
    }
```

**File:** runtime/near-wallet-contract/src/lib.rs (L1-20)
```rust
#![doc = include_str!("../README.md")]
use near_primitives_core::{chains, hash::CryptoHash};
use near_vm_runner::ContractCode;
use std::sync::{Arc, OnceLock};

static MAINNET: WalletContract =
    WalletContract::new(include_bytes!("../res/wallet_contract_mainnet.wasm"));

static TESTNET: WalletContract =
    WalletContract::new(include_bytes!("../res/wallet_contract_testnet.wasm"));

/// Initial version of WalletContract. It was released to testnet, but not mainnet.
/// We still use this one on testnet protocol version 70 for consistency.
/// Example account:
/// https://testnet.nearblocks.io/address/0xcc5a584f545b2ca3ebacc1346556d1f5b82b8fc6
static OLD_TESTNET: WalletContract =
    WalletContract::new(include_bytes!("../res/wallet_contract_testnet_pv70.wasm"));

static LOCALNET: WalletContract =
    WalletContract::new(include_bytes!("../res/wallet_contract_localnet.wasm"));
```

**File:** runtime/near-wallet-contract/src/lib.rs (L68-80)
```rust
/// Get wallet contract code for different Near chains.
pub fn wallet_contract(code_hash: CryptoHash) -> Option<Arc<ContractCode>> {
    LegacyEthWallet::resolve(code_hash).map(|w| w.contract())
}

/// near[wallet contract hash]
pub fn wallet_contract_magic_bytes(chain_id: &str) -> Arc<ContractCode> {
    match chain_id {
        chains::MAINNET => MAINNET.magic_bytes(),
        chains::TESTNET => TESTNET.magic_bytes(),
        _ => LOCALNET.magic_bytes(),
    }
}
```
