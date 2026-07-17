### Title
Missing Chain Identifier in `DelegateAction` Signed Payload Enables Cross-Network Replay - (File: `core/primitives/src/action/delegate.rs`)

---

### Summary

The `DelegateAction` struct (NEP-366 meta transactions) does not include a chain/network identifier in its signed payload. The signing hash is computed over action fields plus a fixed NEP discriminant, but no chain ID. A `SignedDelegateAction` created for one NEAR network (e.g., mainnet) can be replayed on another NEAR network (e.g., testnet) by any unprivileged user who obtains the signed bytes, if the same account and key exist on the target network with a matching nonce.

---

### Finding Description

`DelegateAction` is the core struct for NEAR meta transactions. A user signs it off-chain and hands it to a relayer, which wraps it in a regular transaction and submits it on-chain. The signed payload is computed in `get_nep461_hash()`:

```rust
// core/primitives/src/action/delegate.rs, line 353-357
pub fn get_nep461_hash(&self) -> CryptoHash {
    let signable = SignableMessage::new(&self, SignableMessageType::DelegateAction);
    let bytes = borsh::to_vec(&signable).expect("Failed to deserialize");
    hash(&bytes)
}
```

`SignableMessage` prepends only a `MessageDiscriminant` (the constant NEP number 366) to the serialized action:

```rust
// core/primitives/src/signable_message.rs, line 62-65
pub struct SignableMessage<'a, T> {
    pub discriminant: MessageDiscriminant,
    pub msg: &'a T,
}
```

The `DelegateAction` struct itself contains:

```rust
pub struct DelegateAction {
    pub sender_id: AccountId,
    pub receiver_id: AccountId,
    pub actions: Vec<NonDelegateAction>,
    pub nonce: Nonce,
    pub max_block_height: BlockHeight,
    pub public_key: PublicKey,
}
```

**No chain ID or network ID is present anywhere in the signed payload.** The discriminant `366` is identical on every NEAR network (mainnet, testnet, betanet, private chains). The `max_block_height` is a plain integer with no chain-specific meaning.

By contrast, regular `SignedTransaction` includes a `block_hash` field that is chain-specific (mainnet and testnet have disjoint block hashes), providing implicit cross-chain replay protection. `DelegateAction` deliberately uses `max_block_height` instead of `block_hash` for relayer flexibility, but this removes the only chain-binding mechanism.

The same design gap applies to `DelegateActionV2` / `VersionedSignedDelegateAction`:

```rust
// core/primitives/src/action/delegate.rs, line 180-184
pub fn get_nep461_hash(&self) -> CryptoHash {
    let signable = SignableMessage::new(&self, SignableMessageType::DelegateActionV2);
    let bytes = borsh::to_vec(&signable).expect("failed to serialize");
    hash(&bytes)
}
```

---

### Impact Explanation

An attacker who obtains a `SignedDelegateAction` (intercepted from a public relayer API, a public mempool, or any off-chain channel) can submit it to a different NEAR network via any public RPC node. If the target account exists on that network with the same public key registered and a nonce that satisfies the action's nonce, the runtime will accept and execute the delegated actions.

Concrete corrupted protocol values:
- **Account balance**: a transfer action drains the victim's balance on the target network.
- **Access keys / nonce**: an `AddKey` or `DeleteKey` action modifies the victim's key set and advances the nonce on the target network without the user's intent.
- **Contract state**: a `FunctionCall` action executes arbitrary contract logic under the victim's `predecessor_id` on the target network.

The runtime's `apply_delegate_action` verifies the signature against the hash of the action, but since the hash contains no chain identifier, a valid mainnet signature is also a valid testnet signature for the same payload.

---

### Likelihood Explanation

The preconditions are:
1. The same account ID exists on both networks (very common — developers routinely mirror accounts across mainnet and testnet using the same seed phrases).
2. The same public key is registered on the target network.
3. The nonce on the target network is at the value the action specifies (likely for fresh or low-activity accounts).
4. The `max_block_height` has not been exceeded on the target network (block heights on testnet and mainnet are independent integers; a mainnet action with `max_block_height: 10_000_000` is valid on testnet for a long time).

An attacker can passively collect `SignedDelegateAction` bytes from public relayer services (which accept them over HTTP) and attempt replay on other networks. No validator or node-operator privilege is required — only a public RPC call to submit a transaction.

---

### Recommendation

Include the genesis chain ID (the string identifier from `GenesisConfig::chain_id`, e.g., `"mainnet"`, `"testnet"`) in the `DelegateAction` signed payload, analogous to EIP-712's `chainId` domain separator field. This makes the signing domain disjoint across networks. The field should be added to both `DelegateAction` and `DelegateActionV2`, and included in the borsh-serialized bytes passed to `get_nep461_hash()`. The runtime's `apply_delegate_action` should verify that the chain ID in the action matches the node's own chain ID before accepting the signature.

---

### Proof of Concept

1. Alice signs a `DelegateAction` on mainnet to transfer 10 NEAR to Bob:
   ```
   DelegateAction { sender_id: "alice.near", receiver_id: "bob.near",
     actions: [Transfer { deposit: 10 NEAR }], nonce: 5,
     max_block_height: 200_000_000, public_key: <alice_key> }
   ```
   Hash = `SHA256(borsh([discriminant=0x4000016E] ++ action_bytes))` — identical on every NEAR network.

2. The relayer publishes or leaks the `SignedDelegateAction` bytes.

3. An attacker wraps the same `SignedDelegateAction` in a testnet transaction (the outer transaction's `block_hash` is testnet-specific, but the inner delegate action is not):
   ```rust
   SignedTransaction::from_actions(nonce, relayer, "alice.near", &relayer_signer,
       vec![Action::Delegate(Box::new(signed_delegate_action))],
       testnet_block_hash)
   ```

4. The testnet runtime calls `apply_delegate_action`, which calls `signed.verify()` → `signature.verify(get_nep461_hash(), public_key)`. The hash is identical to mainnet, the signature verifies, and Alice's testnet balance is debited.

**Root cause lines**: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** core/primitives/src/action/delegate.rs (L353-357)
```rust
    pub fn get_nep461_hash(&self) -> CryptoHash {
        let signable = SignableMessage::new(&self, SignableMessageType::DelegateAction);
        let bytes = borsh::to_vec(&signable).expect("Failed to deserialize");
        hash(&bytes)
    }
```

**File:** core/primitives/src/signable_message.rs (L61-65)
```rust
#[derive(BorshSerialize)]
pub struct SignableMessage<'a, T> {
    pub discriminant: MessageDiscriminant,
    pub msg: &'a T,
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
