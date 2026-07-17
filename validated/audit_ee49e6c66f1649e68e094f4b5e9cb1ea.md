### Title
Cross-Network Replay of `DelegateAction` Signatures Due to Missing Chain Binding - (File: core/primitives/src/action/delegate.rs)

### Summary

`DelegateAction` (NEAR meta-transactions, NEP-366) signatures do not include any network-specific identifier. The signed payload contains only a fixed NEP-number discriminant, account IDs, actions, a nonce, a block height ceiling, and a public key — but no chain ID, genesis hash, or block hash. A signed `DelegateAction` produced on one NEAR network (e.g., testnet) can be replayed on another (e.g., mainnet) by any unprivileged relayer, executing the inner actions on behalf of the user on the target network without their consent.

### Finding Description

`DelegateAction::get_nep461_hash()` constructs the signed payload as:

```
SHA-256( borsh( MessageDiscriminant(1<<30 + 366) || DelegateAction ) )
``` [1](#0-0) 

The `MessageDiscriminant` is a fixed constant derived solely from the NEP number (366 for `DelegateAction`, 611 for `DelegateActionV2`): [2](#0-1) [3](#0-2) 

The `DelegateAction` struct itself contains no network-specific field: [4](#0-3) 

By contrast, a regular `SignedTransaction` includes `block_hash` — a hash of a specific block on a specific chain — which implicitly binds the signature to one network: [5](#0-4) 

`DelegateAction` has no equivalent binding. The `max_block_height` field is a plain integer (not a hash), so the same integer is valid on any NEAR network whose current height is below that value.

### Impact Explanation

An attacker who obtains a user's `SignedDelegateAction` from testnet (e.g., by operating a testnet relayer, observing testnet RPC traffic, or receiving it off-chain) can submit it to mainnet via any mainnet relayer. If the preconditions hold, the inner actions execute on mainnet with `sender_id` set to the user's account — enabling unauthorized token transfers, function calls, key additions/deletions, or account deletions on mainnet. The corrupted protocol values are the user's mainnet **account balance**, **access key set**, and **account state**.

### Likelihood Explanation

The preconditions are realistic for developers and power users:

1. **Same account ID on both networks**: Extremely common (`alice.near` exists on both mainnet and testnet).
2. **Same public key on both networks**: Common for developers who reuse keys, and universal for NEAR implicit accounts (whose account ID is derived from the public key).
3. **Valid nonce on mainnet**: If the key is newer on mainnet than on testnet, or if the testnet nonce is ahead of the mainnet nonce for that key, the replayed nonce is accepted.
4. **`max_block_height` valid on mainnet**: If the user sets a generous expiry (e.g., `current_testnet_height + 1_000_000`), and mainnet's current height is below that value, the action is not expired. Mainnet and testnet block heights are independent integers with no guaranteed ordering relationship.

### Recommendation

Include a network-specific identifier in the `DelegateAction` signed payload. The most natural choice is the **genesis block hash** (which uniquely identifies a NEAR network) or the **chain ID string** (e.g., `"mainnet"`, `"testnet"`). This mirrors how regular `SignedTransaction` achieves implicit chain binding via `block_hash`, and is analogous to EIP-155's `chain_id` inclusion in Ethereum transaction signatures. The `SignableMessage` / `MessageDiscriminant` scheme in `core/primitives/src/signable_message.rs` is the right place to introduce this binding. [6](#0-5) 

### Proof of Concept

1. Alice has account `alice.near` on both testnet and mainnet, using the same ED25519 key pair. Her mainnet key nonce is 5; her testnet key nonce is 10.
2. Alice signs a testnet `DelegateAction` transferring 100 NEAR to `bob.near`, with `nonce = 11` and `max_block_height = 999_999_999`.
3. The signed payload is `SHA-256(borsh(0x6E010000 || DelegateAction{sender_id="alice.near", receiver_id="bob.near", actions=[Transfer(100 NEAR)], nonce=11, max_block_height=999_999_999, public_key=...}))` — identical on any NEAR network.
4. An attacker intercepts the `SignedDelegateAction` from the testnet relayer.
5. The attacker wraps it in a mainnet transaction (attacker pays gas) and submits it to mainnet RPC.
6. Mainnet runtime calls `SignedDelegateAction::verify()`: [7](#0-6) 

7. Verification passes (same hash, same key). Nonce 11 > 5 (mainnet current nonce). Block height 999_999_999 > mainnet current height. The transfer executes, draining Alice's mainnet balance.

### Citations

**File:** core/primitives/src/action/delegate.rs (L46-64)
```rust
pub struct DelegateAction {
    /// Signer of the delegated actions
    pub sender_id: AccountId,
    /// Receiver of the delegated actions.
    pub receiver_id: AccountId,
    /// List of actions to be executed.
    ///
    /// With the meta transactions MVP defined in NEP-366, nested
    /// DelegateActions are not allowed. A separate type is used to enforce it.
    pub actions: Vec<NonDelegateAction>,
    /// Nonce to ensure that the same delegate action is not sent twice by a
    /// relayer and should match for given account's `public_key`.
    /// After this action is processed it will increment.
    pub nonce: Nonce,
    /// The maximal height of the block in the blockchain below which the given DelegateAction is valid.
    pub max_block_height: BlockHeight,
    /// Public key used to sign this delegated action.
    pub public_key: PublicKey,
}
```

**File:** core/primitives/src/action/delegate.rs (L83-95)
```rust
impl SignedDelegateAction {
    pub fn verify(&self) -> bool {
        let delegate_action = &self.delegate_action;
        let hash = delegate_action.get_nep461_hash();
        let public_key = &delegate_action.public_key;

        self.signature.verify(hash.as_ref(), public_key)
    }

    pub fn sign(singer: &Signer, delegate_action: DelegateAction) -> Self {
        let signature = singer.sign(delegate_action.get_nep461_hash().as_bytes());
        Self { delegate_action, signature }
    }
```

**File:** core/primitives/src/action/delegate.rs (L349-357)
```rust
    /// Delegate action hash used for NEP-461 signature scheme which tags
    /// different messages before hashing
    ///
    /// For more details, see: [NEP-461](https://github.com/near/NEPs/pull/461)
    pub fn get_nep461_hash(&self) -> CryptoHash {
        let signable = SignableMessage::new(&self, SignableMessageType::DelegateAction);
        let bytes = borsh::to_vec(&signable).expect("Failed to deserialize");
        hash(&bytes)
    }
```

**File:** core/primitives/src/signable_message.rs (L18-25)
```rust
const MIN_ON_CHAIN_DISCRIMINANT: u32 = 1 << 30;
const MAX_ON_CHAIN_DISCRIMINANT: u32 = (1 << 31) - 1;
const MIN_OFF_CHAIN_DISCRIMINANT: u32 = 1 << 31;
const MAX_OFF_CHAIN_DISCRIMINANT: u32 = u32::MAX;

// NEPs currently included in the scheme
const NEP_366_META_TRANSACTIONS: u32 = 366;
const NEP_611_GAS_KEYS: u32 = 611;
```

**File:** core/primitives/src/signable_message.rs (L61-107)
```rust
#[derive(BorshSerialize)]
pub struct SignableMessage<'a, T> {
    pub discriminant: MessageDiscriminant,
    pub msg: &'a T,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
#[non_exhaustive]
pub enum SignableMessageType {
    /// A delegate action, intended for a relayer to included it in an action list of a transaction.
    DelegateAction,
    /// A delegate action with gas key support, intended for a relayer to include it in an action
    /// list of a transaction.
    DelegateActionV2,
}

#[derive(thiserror::Error, Debug)]
#[non_exhaustive]
pub enum ReadDiscriminantError {
    #[error("does not fit any known categories")]
    UnknownMessageType,
    #[error("NEP {0} does not have a known on-chain use")]
    UnknownOnChainNep(u32),
    #[error("NEP {0} does not have a known off-chain use")]
    UnknownOffChainNep(u32),
    #[error("discriminant is in the range for transactions")]
    TransactionFound,
}

#[derive(thiserror::Error, Debug)]
#[non_exhaustive]
pub enum CreateDiscriminantError {
    #[error("nep number {0} is too big")]
    NepTooLarge(u32),
}

impl<'a, T: BorshSerialize> SignableMessage<'a, T> {
    pub fn new(msg: &'a T, ty: SignableMessageType) -> Self {
        let discriminant = ty.into();
        Self { discriminant, msg }
    }

    pub fn sign(&self, signer: &Signer) -> Signature {
        let bytes = borsh::to_vec(&self).expect("Failed to deserialize");
        let hash = hash(&bytes);
        signer.sign(hash.as_bytes())
    }
```

**File:** core/primitives/src/signable_message.rs (L217-228)
```rust
impl From<SignableMessageType> for MessageDiscriminant {
    fn from(ty: SignableMessageType) -> Self {
        // unwrapping here is ok, we know the constant NEP numbers used are in range
        match ty {
            SignableMessageType::DelegateAction => {
                MessageDiscriminant::new_on_chain(NEP_366_META_TRANSACTIONS).unwrap()
            }
            SignableMessageType::DelegateActionV2 => {
                MessageDiscriminant::new_on_chain(NEP_611_GAS_KEYS).unwrap()
            }
        }
    }
```

**File:** core/primitives/src/transaction.rs (L33-48)
```rust
pub struct TransactionV0 {
    /// An account on which behalf transaction is signed
    pub signer_id: AccountId,
    /// A public key of the access key which was used to sign an account.
    /// Access key holds permissions for calling certain kinds of actions.
    pub public_key: PublicKey,
    /// Nonce is used to determine order of transaction in the pool.
    /// It increments for a combination of `signer_id` and `public_key`
    pub nonce: Nonce,
    /// Receiver account for this transaction
    pub receiver_id: AccountId,
    /// The hash of the block in the blockchain on top of which the given transaction is valid
    pub block_hash: CryptoHash,
    /// A list of actions to be applied
    pub actions: Vec<Action>,
}
```
