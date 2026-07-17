### Title
`DelegateAction` Signed Payload Lacks Chain/Network Domain Separation Enabling Cross-Network Replay - (`File: core/primitives/src/action/delegate.rs`)

### Summary
`DelegateAction` (NEP-366 meta transactions) and `DelegateActionV2` (NEP-611 gas keys) produce signatures that commit to no chain identifier. A malicious relayer who receives a `SignedDelegateAction` created on one NEAR network (e.g., testnet) can wrap it in a fresh outer transaction and submit it to a different NEAR network (e.g., mainnet), where it will pass signature verification and execute the inner actions on behalf of the original signer.

### Finding Description

`DelegateAction::get_nep461_hash()` constructs the signed digest by serializing a `SignableMessage` that contains only a `MessageDiscriminant` (a NEP number) and the action body itself:

```rust
pub fn get_nep461_hash(&self) -> CryptoHash {
    let signable = SignableMessage::new(&self, SignableMessageType::DelegateAction);
    let bytes = borsh::to_vec(&signable).expect("Failed to deserialize");
    hash(&bytes)
}
``` [1](#0-0) 

`SignableMessage` is defined as:

```rust
pub struct SignableMessage<'a, T> {
    pub discriminant: MessageDiscriminant,
    pub msg: &'a T,
}
``` [2](#0-1) 

The `MessageDiscriminant` is a single `u32` encoding the NEP number (366 for `DelegateAction`, 611 for `DelegateActionV2`): [3](#0-2) [4](#0-3) 

The `DelegateAction` body itself contains `sender_id`, `receiver_id`, `actions`, `nonce`, `max_block_height`, and `public_key` — but **no chain ID, no genesis hash, and no network identifier**: [5](#0-4) 

The same is true for `DelegateActionV2`: [6](#0-5) 

Signature verification in `SignedDelegateAction::verify()` and `VersionedSignedDelegateAction::verify()` checks only that the signature matches the NEP-discriminant-prefixed hash of the action body: [7](#0-6) [8](#0-7) 

The outer `SignedTransaction` that carries the `DelegateAction` does include a `block_hash` binding it to a specific chain, but that binding is on the **relayer's** transaction, not on the user's inner signed payload. The runtime's `apply_delegate_action` / `validate_delegate_action_key` only checks nonce, `max_block_height`, access-key existence, and the chain-agnostic signature above — no chain-specific field is ever verified against the inner delegate signature: [9](#0-8) [10](#0-9) 

### Impact Explanation

An unprivileged malicious relayer who receives a `SignedDelegateAction` (or `VersionedSignedDelegateAction`) created by a user on network A can:

1. Wrap it in a brand-new `SignedTransaction` on network B (the relayer signs only the outer transaction, which is chain-bound; the inner delegate signature is unchanged).
2. Submit it to network B's RPC.
3. The runtime on network B will verify the inner delegate signature, find it valid (because no chain ID is committed), check the nonce against the sender's access key on network B, and execute the inner actions.

Concrete corrupted protocol values: the sender's **account state on network B** — nonce, NEAR balance, fungible-token balances (via `ft_transfer` calls), and access keys — is mutated by actions the user never authorized for that network. The nonce on network B is also permanently advanced, potentially blocking legitimate future meta-transactions.

Preconditions that are realistic in practice:
- The user holds the same named account and key pair on both testnet and mainnet (extremely common; NEAR account names are human-readable and users routinely mirror them).
- The `max_block_height` in the delegate action is set to a sufficiently large value (standard relayer practice to avoid premature expiry).
- The nonce in the delegate action is valid on network B (e.g., the account was recently created on mainnet and its access-key nonce is still low).

### Likelihood Explanation

Medium. The attack requires a malicious relayer — a role that is explicitly part of the meta-transaction trust model and that any third party can occupy. Users routinely use the same account name and key on testnet and mainnet. Relayer software that operates on multiple networks (e.g., a cross-network relayer service) is a realistic deployment scenario. The `max_block_height` field is typically set far in the future by SDK tooling, keeping the window open for extended periods.

### Recommendation

Include a chain/network identifier in the signed preimage. The cleanest approach is to add the genesis block hash (or a dedicated `chain_id` string from `GenesisConfig`) to `SignableMessage` or directly to `DelegateAction`/`DelegateActionV2`:

```rust
// In get_nep461_hash(), bind to the genesis hash or chain_id:
pub fn get_nep461_hash(&self, chain_id: &str) -> CryptoHash {
    let signable = SignableMessage::new(
        &(chain_id, &self),
        SignableMessageType::DelegateAction,
    );
    let bytes = borsh::to_vec(&signable).expect("Failed to serialize");
    hash(&bytes)
}
```

Alternatively, add a `chain_id: String` field directly to `DelegateAction` and `DelegateActionV2` (as a protocol-version-gated addition), mirroring how `SignedTransaction` is already chain-bound through its `block_hash`.

### Proof of Concept

1. Alice holds account `alice.near` on both testnet and mainnet with the same ED25519 key. Her mainnet access-key nonce is 0 (freshly created account).
2. Alice signs a `DelegateAction` on testnet: `{sender_id: "alice.near", receiver_id: "token.testnet", actions: [Transfer{1 NEAR}], nonce: 1, max_block_height: 999_999_999, public_key: <alice_key>}`. She sends it to a testnet relayer.
3. A malicious relayer intercepts the `SignedDelegateAction`. It constructs a mainnet `SignedTransaction` with `receiver_id = "alice.near"` and `actions = [Action::Delegate(signed_delegate_action)]`, signing only the outer transaction with its own mainnet key.
4. The malicious relayer submits this to mainnet RPC (`broadcast_tx_async`).
5. The mainnet runtime calls `apply_delegate_action`. It calls `signed_delegate_action.verify()` → `get_nep461_hash()` → produces the same hash as on testnet (no chain ID in the preimage) → signature check passes.
6. `validate_delegate_action_key` checks nonce 1 > current nonce 0 ✓, checks `max_block_height` ✓, finds the access key ✓.
7. The inner `Transfer{1 NEAR}` executes on mainnet, draining Alice's mainnet balance — an action she never authorized for mainnet. [1](#0-0) [11](#0-10) [10](#0-9)

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

**File:** core/primitives/src/action/delegate.rs (L83-90)
```rust
impl SignedDelegateAction {
    pub fn verify(&self) -> bool {
        let delegate_action = &self.delegate_action;
        let hash = delegate_action.get_nep461_hash();
        let public_key = &delegate_action.public_key;

        self.signature.verify(hash.as_ref(), public_key)
    }
```

**File:** core/primitives/src/action/delegate.rs (L119-133)
```rust
pub struct DelegateActionV2 {
    /// Signer of the delegated actions
    pub sender_id: AccountId,
    /// Receiver of the delegated actions.
    pub receiver_id: AccountId,
    /// List of actions to be executed.
    pub actions: Vec<NonDelegateAction>,
    /// Nonce of the signing key, advanced when this action is processed. For
    /// a gas key it also selects which of the parallel nonces to advance.
    pub nonce: TransactionNonce,
    /// The maximal height of the block in the blockchain below which the given DelegateActionV2 is valid.
    pub max_block_height: BlockHeight,
    /// Public key used to sign this delegated action.
    pub public_key: PublicKey,
}
```

**File:** core/primitives/src/action/delegate.rs (L210-214)
```rust
impl VersionedSignedDelegateAction {
    pub fn verify(&self) -> bool {
        let hash = self.delegate_action.get_nep461_hash();
        self.signature.verify(hash.as_ref(), self.delegate_action.public_key())
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

**File:** core/primitives/src/signable_message.rs (L51-54)
```rust
pub struct MessageDiscriminant {
    /// The unique prefix, serialized in little-endian by borsh.
    discriminant: u32,
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

**File:** core/primitives/src/signable_message.rs (L97-108)
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

**File:** runtime/runtime/src/actions.rs (L530-545)
```rust
/// Validate access key which was used for signing DelegateAction:
///
/// - Checks whether the access key is present fo given public_key and sender_id.
/// - Validates nonce and updates it if it's ok.
/// - Validates access key permissions.
fn validate_delegate_action_key(
    state_update: &mut TrieUpdate,
    apply_state: &ApplyState,
    delegate_action: VersionedDelegateActionRef<'_>,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
    let sender_id = delegate_action.sender_id();
    let public_key = delegate_action.public_key();
    // 'sender_id' account existence must be checked by a caller
    let mut access_key = match get_access_key(state_update, sender_id, public_key)? {
        Some(access_key) => access_key,
```

**File:** runtime/runtime/src/actions.rs (L604-622)
```rust
    if delegate_nonce.nonce() <= current_nonce {
        result.result = Err(ActionErrorKind::DelegateActionInvalidNonce {
            delegate_nonce: delegate_nonce.nonce(),
            ak_nonce: current_nonce,
        }
        .into());
        return Ok(());
    }

    let upper_bound = apply_state.block_height
        * near_primitives::account::AccessKey::ACCESS_KEY_NONCE_RANGE_MULTIPLIER;
    if delegate_nonce.nonce() >= upper_bound {
        result.result = Err(ActionErrorKind::DelegateActionNonceTooLarge {
            delegate_nonce: delegate_nonce.nonce(),
            upper_bound,
        }
        .into());
        return Ok(());
    }
```
