### Title
`DelegateAction` (Meta-Transaction) Signed Payload Lacks Chain-ID Domain Separation, Enabling Cross-Network Signature Replay - (File: `core/primitives/src/action/delegate.rs`, `core/primitives/src/signable_message.rs`)

### Summary

`DelegateAction` and `DelegateActionV2` (NEP-366/NEP-611 meta-transactions) are signed over a payload that contains no chain-specific context — no `chain_id`, no network identifier, no genesis hash. A `SignedDelegateAction` produced on NEAR testnet is cryptographically valid on NEAR mainnet (or any fork) whenever the same account and key exist on both networks and the nonce is still acceptable on the target chain. An unprivileged attacker who observes a signed delegate action (e.g., as a relayer, or by monitoring the testnet mempool) can replay it on a different NEAR network to execute arbitrary actions on behalf of the victim.

### Finding Description

`DelegateAction::get_nep461_hash()` constructs the signed digest as:

```
SHA-256( borsh( MessageDiscriminant(NEP_366) ) || borsh( DelegateAction ) )
``` [1](#0-0) 

`SignableMessage::new()` wraps the payload with only a fixed 4-byte discriminant (`1 << 30 + 366`): [2](#0-1) 

The `DelegateAction` struct itself contains no chain-specific field: [3](#0-2) 

The same is true for `VersionedDelegateActionPayload::get_nep461_hash()` used by `DelegateActionV2`: [4](#0-3) 

By contrast, regular `SignedTransaction` includes a `block_hash` field that is chain-specific (a recent block hash from the specific network), providing implicit cross-chain replay protection: [5](#0-4) 

`DelegateAction` has no equivalent binding. The `max_block_height` field is a block height integer, not a block hash, and block heights are not chain-specific — mainnet and testnet have comparable heights.

The runtime verifies the signature at `apply_delegate_action` → `signed_delegate_action.verify()`, which only checks the signature against the chain-agnostic hash: [6](#0-5) 

### Impact Explanation

An attacker who obtains a `SignedDelegateAction` produced on testnet can submit it on mainnet. If the victim's mainnet access key nonce is lower than the nonce embedded in the delegate action (common when a user is more active on testnet), the runtime will:

1. Accept the signature as valid (same key, same hash, no chain binding).
2. Advance the victim's mainnet access key nonce.
3. Execute the inner actions — which may include `Transfer`, `AddKey`, `DeleteKey`, `FunctionCall`, or `DeleteAccount` — with `predecessor_id` set to the victim's account.

The corrupted protocol values are: the victim's on-chain access key nonce (incremented), their account balance (drained by Transfer), their access key set (modified by AddKey/DeleteKey), and any contract state mutated by FunctionCall. All of these are irreversible once the receipt executes.

### Likelihood Explanation

- Many users share the same named account and key pair across testnet and mainnet (standard practice for developers and power users).
- A malicious relayer sees every `SignedDelegateAction` before it is submitted; this is the normal meta-transaction flow.
- A testnet mempool observer can collect signed delegate actions at zero cost.
- The nonce condition (mainnet nonce < delegate nonce) is satisfied whenever the victim is more active on testnet than mainnet, which is the typical developer workflow.
- `max_block_height` does not help: mainnet and testnet block heights are in the same order of magnitude, so a testnet-signed action with a generous `max_block_height` remains valid on mainnet for the same window.

### Recommendation

**Short term:** Include the chain's genesis hash or a canonical `chain_id` string in the `SignableMessage` payload for `DelegateAction` and `DelegateActionV2`. This can be done by adding a `chain_id: String` field to `DelegateAction`/`DelegateActionV2`, or by incorporating it into the `SignableMessage` wrapper before hashing.

**Long term:** Standardize a network-scoped signing domain (analogous to EIP-712's `domainSeparator`) for all off-chain-signed NEAR messages, so that any future signable message type is automatically bound to a specific network.

### Proof of Concept

1. Alice has account `alice.near` with key `ed25519:K` on both testnet and mainnet. Her mainnet access key nonce is 5; her testnet nonce is 20.
2. Alice signs a `DelegateAction` on testnet: `sender_id=alice.near, receiver_id=bob.near, actions=[Transfer(100 NEAR)], nonce=21, max_block_height=200_000_000, public_key=K`.
3. Eve (a malicious relayer) receives this `SignedDelegateAction` off-chain.
4. Eve submits it on mainnet inside a transaction addressed to `alice.near`.
5. `apply_delegate_action` calls `signed_delegate_action.verify()` → passes (same key, same chain-agnostic hash).
6. Nonce check: `21 > 5` → passes.
7. Height check: mainnet block height ≈ 130M < 200M → passes.
8. A new receipt is created: `predecessor=alice.near, receiver=bob.near, actions=[Transfer(100 NEAR)]`.
9. 100 NEAR is transferred from Alice's mainnet account to Bob without Alice's mainnet consent.

The root cause is the absence of any chain-binding in `DelegateAction::get_nep461_hash()` at `core/primitives/src/action/delegate.rs:353-357` and `VersionedDelegateActionPayload::get_nep461_hash()` at `core/primitives/src/action/delegate.rs:180-184`, both of which delegate to `SignableMessage` at `core/primitives/src/signable_message.rs:97-107` without including a network identifier.

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

**File:** core/primitives/src/action/delegate.rs (L180-184)
```rust
    pub fn get_nep461_hash(&self) -> CryptoHash {
        let signable = SignableMessage::new(&self, SignableMessageType::DelegateActionV2);
        let bytes = borsh::to_vec(&signable).expect("failed to serialize");
        hash(&bytes)
    }
```

**File:** core/primitives/src/action/delegate.rs (L353-357)
```rust
    pub fn get_nep461_hash(&self) -> CryptoHash {
        let signable = SignableMessage::new(&self, SignableMessageType::DelegateAction);
        let bytes = borsh::to_vec(&signable).expect("Failed to deserialize");
        hash(&bytes)
    }
```

**File:** core/primitives/src/signable_message.rs (L97-107)
```rust
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

**File:** core/primitives/src/transaction.rs (L130-133)
```rust
    pub receiver_id: AccountId,
    /// The hash of the block in the blockchain on top of which the given transaction is valid
    pub block_hash: CryptoHash,
    /// A list of actions to be applied
```

**File:** runtime/runtime/src/actions.rs (L430-433)
```rust
    if !signed_delegate_action.verify() {
        result.result = Err(ActionErrorKind::DelegateActionInvalidSignature.into());
        return Ok(());
    }
```
