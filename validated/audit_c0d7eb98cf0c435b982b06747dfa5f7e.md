### Title
NEP-366/NEP-611 `DelegateAction` signatures omit any chain-specific binding, enabling cross-chain signature replay - (File: `core/primitives/src/action/delegate.rs`)

### Summary
The meta-transaction signature scheme used for `DelegateAction`/`DelegateActionV2` (NEP-366/NEP-611, implemented via NEP-461 `SignableMessage`) hashes only the NEP discriminant plus the delegate action fields (`sender_id`, `receiver_id`, `actions`, `nonce`, `max_block_height`, `public_key`). No genesis hash, chain id, or block hash tied to a specific chain instance is included in the signed payload, unlike ordinary `SignedTransaction`s.

### Finding Description
`SignedDelegateAction::verify`/`sign` and `VersionedSignedDelegateAction::verify`/`sign` derive their signed hash from `DelegateAction::get_nep461_hash` / `VersionedDelegateActionPayload::get_nep461_hash`, which wraps the action in a `SignableMessage` and borsh-serializes only the discriminant and the action struct: [1](#0-0) [2](#0-1) 

The `SignableMessage` construction confirms nothing beyond the NEP discriminant and the message body is bound into the hash: [3](#0-2) [4](#0-3) 

By contrast, ordinary NEAR transactions include a `block_hash` field that anchors the signature to a specific chain's recent block, giving them chain-specific replay protection that ties the signature to the exact chain fork/state the signer observed. `DelegateAction` replaces this with a bare `max_block_height: BlockHeight` — an integer with no cryptographic tie to any particular chain's block hash or genesis: [5](#0-4) 

On execution, `apply_delegate_action` only checks the signature, expiry height, and sender/receiver match, then defers replay protection entirely to the access key nonce stored in that chain's own state trie: [6](#0-5) [7](#0-6) 

Because neither the signed payload nor the validation logic commits to a chain/genesis identifier, a `SignedDelegateAction`/`VersionedSignedDelegateAction` produced for one NEAR network instance is equally valid on any other independent chain where the same `sender_id` account exists with the same public key and an access key nonce still below the signed nonce (e.g., a forked/cloned chain state, a sandbox/testnet environment seeded from mainnet state, or any scenario where the same account/key pair and unconsumed nonce coexist on more than one chain). A relayer (or anyone who can observe the signed message, since relayers are meant to broadcast it) can replay the identical bytes on the second chain to execute the same delegated actions there without a fresh signature from the account owner.

### Impact Explanation
If the same account id and access key nonce state exist on two independently-operating NEAR chains (forked/cloned state, sandbox environments, or post-split networks), a signed meta-transaction authorizing a specific action (e.g., a transfer, function call with deposit, or key/account management action) can be replayed unmodified on the second chain, causing unauthorized action execution and state/balance changes the signer did not intend for that chain. This matches the "unauthorized state or balance change" impact class via `apply_delegate_action`'s receipt generation, which spends the relayer's prepaid gas/deposit and executes attacker-selected `actions` from the delegate payload: [8](#0-7) 

### Likelihood Explanation
Exploitation requires two chains that both recognize the same `sender_id`/access-key/nonce state (e.g., testnet/sandbox forks seeded from the same state, or a chain split), and a relayer or observer willing to resubmit the exact signed bytes to the second chain. Within a single canonical NEAR chain this cannot be exploited because nonce state is shared and strictly increasing, so likelihood is limited to multi-chain/forked-state deployments rather than mainline mainnet operation.

### Recommendation
Bind the NEP-461 `SignableMessage`/`DelegateAction` hash to a chain-specific identifier (e.g., the genesis hash or `chain_id` string) in addition to `max_block_height`, mirroring how `SignedTransaction.block_hash` anchors ordinary transactions to a specific chain, so a signature produced for one chain instance cannot be replayed on another that happens to share account/key/nonce state.

### Proof of Concept
1. Clone or fork a NEAR chain's state (or spin up a sandbox/testnet instance seeded from the same account/access-key state) so account `alice.near` with public key `K` and access key nonce `N` exists identically on chain A and chain B.
2. On chain A, `alice.near` signs a `DelegateAction{sender_id: alice.near, receiver_id: bob.near, actions: [...], nonce: N+1, max_block_height: H, public_key: K}` via `SignedDelegateAction::sign` / `VersionedSignedDelegateAction::sign`, producing signature `S` over `get_nep461_hash()` as shown in [9](#0-8) .
3. A relayer submits this `Action::Delegate`/`Action::DelegateV2` in an outer transaction on chain A; it executes normally.
4. The same relayer resubmits the identical `SignedDelegateAction` bytes as an outer transaction on chain B (where `H` is still a future block height and `N+1` still exceeds the stored access key nonce). `apply_delegate_action`'s checks — signature verify, `max_block_height`, sender/receiver match, and nonce comparison against chain B's own stored nonce — all pass because none of them reference any chain-specific value, per `validate_delegate_action_key`: [10](#0-9) 
5. The delegated actions execute a second time on chain B without any new authorization from `alice.near`.

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

**File:** core/primitives/src/action/delegate.rs (L83-96)
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
}
```

**File:** core/primitives/src/action/delegate.rs (L176-185)
```rust
    /// Delegate action hash used for NEP-461 signature scheme which tags
    /// different messages before hashing
    ///
    /// For more details, see: [NEP-461](https://github.com/near/NEPs/pull/461)
    pub fn get_nep461_hash(&self) -> CryptoHash {
        let signable = SignableMessage::new(&self, SignableMessageType::DelegateActionV2);
        let bytes = borsh::to_vec(&signable).expect("failed to serialize");
        hash(&bytes)
    }
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

**File:** runtime/runtime/src/actions.rs (L458-474)
```rust
    if !signed_delegate_action.verify() {
        result.result = Err(ActionErrorKind::DelegateActionInvalidSignature.into());
        return Ok(());
    }
    let delegate_action = signed_delegate_action.delegate_action();
    if apply_state.block_height > delegate_action.max_block_height() {
        result.result = Err(ActionErrorKind::DelegateActionExpired.into());
        return Ok(());
    }
    if delegate_action.sender_id().as_str() != sender_id.as_str() {
        result.result = Err(ActionErrorKind::DelegateActionSenderDoesNotMatchTxReceiver {
            sender_id: delegate_action.sender_id().clone(),
            receiver_id: sender_id.clone(),
        }
        .into());
        return Ok(());
    }
```

**File:** runtime/runtime/src/actions.rs (L483-497)
```rust
    // Generate a new receipt from DelegateAction.
    let new_receipt = Receipt::V0(ReceiptV0 {
        predecessor_id: sender_id.clone(),
        receiver_id: delegate_action.receiver_id().clone(),
        receipt_id: CryptoHash::default(),

        receipt: ReceiptEnum::Action(ActionReceipt {
            signer_id: action_receipt.signer_id().clone(),
            signer_public_key: action_receipt.signer_public_key().clone(),
            gas_price: action_receipt.gas_price(),
            output_data_receivers: vec![],
            input_data_ids: vec![],
            actions: delegate_action.get_actions(),
        }),
    });
```

**File:** runtime/runtime/src/actions.rs (L558-568)
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
```

**File:** runtime/runtime/src/actions.rs (L586-639)
```rust
    // A plain nonce advances the single access_key.nonce and forbids gas keys;
    // a gas key nonce advances one of the gas key's nonces selected by
    // nonce_index.
    let delegate_nonce = delegate_action.nonce();
    let (current_nonce, nonce_update) = match delegate_nonce {
        TransactionNonce::Nonce { .. } => {
            if access_key.gas_key_info().is_some() {
                result.result = Err(ActionErrorKind::DelegateActionAccessKeyError(
                    InvalidAccessKeyError::DelegateActionRequiresNonGasKey,
                )
                .into());
                return Ok(());
            }
            (access_key.nonce, DelegateNonceUpdate::AccessKey)
        }
        TransactionNonce::GasKeyNonce { nonce_index, .. } => {
            let Some(gas_key_info) = access_key.gas_key_info() else {
                result.result = Err(ActionErrorKind::DelegateActionAccessKeyError(
                    InvalidAccessKeyError::DelegateActionRequiresGasKey,
                )
                .into());
                return Ok(());
            };
            if nonce_index >= gas_key_info.num_nonces {
                result.result = Err(ActionErrorKind::DelegateActionInvalidNonceIndex {
                    nonce_index,
                    num_nonces: gas_key_info.num_nonces,
                }
                .into());
                return Ok(());
            }
            // The index is range-checked above and gas keys initialize every
            // nonce row at creation, so a missing row is inconsistent state.
            let current_nonce =
                get_gas_key_nonce(state_update, sender_id, public_key, nonce_index)?.ok_or_else(
                    || {
                        StorageError::StorageInconsistentState(format!(
                            "gas key nonce row missing for {} {} at in-range index {nonce_index} (num_nonces {})",
                            sender_id, public_key, gas_key_info.num_nonces,
                        ))
                    },
                )?;
            (current_nonce, DelegateNonceUpdate::GasKey { nonce_index })
        }
    };

    if delegate_nonce.nonce() <= current_nonce {
        result.result = Err(ActionErrorKind::DelegateActionInvalidNonce {
            delegate_nonce: delegate_nonce.nonce(),
            ak_nonce: current_nonce,
        }
        .into());
        return Ok(());
    }
```
