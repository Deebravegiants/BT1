### Title
Missing chain/network domain separator in NEP-366/NEP-611 meta-transaction (`DelegateAction`) signature scheme allows cross-network signature replay - (File: core/primitives/src/signable_message.rs)

### Summary
`SignedDelegateAction`/`VersionedSignedDelegateAction` (NEAR meta-transactions) are authenticated by signing a hash that only binds `sender_id`, `receiver_id`, `actions`, `nonce`, `max_block_height`, `public_key`, and a fixed NEP-number "message discriminant". No network/chain-specific value (e.g. a genesis hash or chain id) is included in the signed payload, so the same signature is valid on any nearcore-based deployment where the signer's account/key and nonce state happen to match — mirroring exactly the "raw hash without EIP-712 domain separator" bug class described in the external report.

### Finding Description
The signing/verification logic lives in `core/primitives/src/signable_message.rs` and `core/primitives/src/action/delegate.rs`: [1](#0-0) 

`SignableMessage` wraps the message with only a `MessageDiscriminant` (a constant per NEP number, e.g. `NEP_366_META_TRANSACTIONS`/`NEP_611_GAS_KEYS`) and the message body itself: [2](#0-1) [3](#0-2) 

Verification (`SignedDelegateAction::verify` / `VersionedSignedDelegateAction::verify`) simply recomputes this same hash and checks the ed25519 signature against `public_key` embedded in the action — again with no chain-specific input: [4](#0-3) [5](#0-4) 

At execution time, `apply_delegate_action` in `runtime/runtime/src/actions.rs` only checks the signature, `max_block_height` (a plain block-height integer, not a chain-bound hash), sender/receiver match, and then validates/increments the local per-account nonce via `validate_delegate_action_key` — none of which are unique to a specific chain deployment: [6](#0-5) 

By contrast, ordinary `SignedTransaction`s include a recent `block_hash` from the chain they are submitted to, which is intrinsically chain-specific and provides de-facto replay protection across independently-genesis'd networks. The inner `DelegateAction` payload that a user actually signs has no equivalent binding — it only carries a plain `max_block_height` number and a fixed protocol/NEP discriminant, which are identical across every nearcore-based network. This is confirmed by the repo's own `tools/mirror/src/genesis.rs`, which — when re-signing delegate actions while mirroring one chain's state to another — deliberately maps to a *different* derived secret key rather than reusing the original signature, implicitly acknowledging that raw byte-for-byte reuse of an original signed `DelegateAction` across networks would otherwise still verify: [7](#0-6) [8](#0-7) 

### Impact Explanation
Any relayer or observer who obtains a user's signed `DelegateAction`/`DelegateActionV2` (meta-transaction) intended for one nearcore-based network can wrap it into a normal `SignedTransaction` (with a valid recent `block_hash` and relayer-paid gas) and submit it on **any other** nearcore-based network where the victim's `sender_id` account exists with the same `public_key` and the nonce has not yet advanced past the value in the delegate action (e.g. forked/mirrored testnets, disaster-recovery/migrated chains, or any deployment sharing genesis-derived account/key state with another). Because the signed payload never binds to a specific chain, the runtime accepts and executes the replayed actions (transfers, function calls, key management, etc.) exactly as if the user had authorized them on that network — an unauthorized state/balance change attributable to the victim's account on a network the user never intended to interact with.

### Likelihood Explanation
Exploitation requires a scenario where the same account id and access key/nonce state exists on two independently-operated nearcore chains (e.g. chain forks, disaster-recovery restores, or migrated/mirrored networks such as the one explicitly supported by `tools/mirror`). This is a narrower precondition than the classic EVM cross-chain replay case (where any EOA private key trivially controls the "same" address on every EVM chain), so likelihood is lower than the original Solidity finding, but the underlying root cause — signing a hash with no chain-binding domain separator — is structurally identical, and the codebase's own mirroring tool demonstrates this exact scenario is a real operational concern for nearcore deployments.

### Recommendation
Include a chain-specific value (e.g. the genesis hash, or an explicit network/chain identifier already used to distinguish networks) as part of the `SignableMessage`/`DelegateAction` payload that is hashed and signed, so meta-transaction signatures are cryptographically bound to one specific chain, in line with the EIP-712-style domain-separation approach recommended in the referenced report. This should be introduced as part of the ongoing NEP-461 standardization effort referenced in `core/primitives/src/signable_message.rs`.

### Proof of Concept
1. On network A, a user account `alice.near` signs a `DelegateAction` (e.g. via `SignedDelegateAction::sign`) authorizing a transfer/function call, intended to be relayed only on network A.
2. Network B is a nearcore-based deployment that shares `alice.near`'s account id, `public_key`, and current access-key nonce with network A (e.g. a forked/mirrored/disaster-recovery chain, as supported by `tools/mirror`).
3. An attacker/relayer takes the exact same `SignedDelegateAction` bytes and submits them via RPC to network B inside a fresh `SignedTransaction` (`Action::Delegate`) with a valid recent `block_hash` from network B and relayer-paid gas.
4. `apply_delegate_action` on network B validates the signature (`signed_delegate_action.verify()`), checks `max_block_height` against B's current height, matches `sender_id`, and validates the nonce against B's local access-key state — all of which pass because none of these checks are chain-specific — and the action executes on network B without the user's authorization for that network.

### Citations

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

**File:** core/primitives/src/action/delegate.rs (L210-220)
```rust
impl VersionedSignedDelegateAction {
    pub fn verify(&self) -> bool {
        let hash = self.delegate_action.get_nep461_hash();
        self.signature.verify(hash.as_ref(), self.delegate_action.public_key())
    }

    pub fn sign(signer: &Signer, delegate_action: VersionedDelegateActionPayload) -> Self {
        let signature = signer.sign(delegate_action.get_nep461_hash().as_bytes());
        Self { delegate_action, signature }
    }
}
```

**File:** core/primitives/src/action/delegate.rs (L349-358)
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
}
```

**File:** runtime/runtime/src/actions.rs (L437-476)
```rust
pub(crate) fn apply_delegate_action(
    state_update: &mut TrieUpdate,
    apply_state: &ApplyState,
    action_receipt: &VersionedActionReceipt,
    sender_id: &AccountId,
    signed_delegate_action: VersionedSignedDelegateActionRef<'_>,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
    // The inner delegate signature is verified below, here on the receiver shard.
    // Meter its verification compute against this shard's `compute_limit`; the gas
    // for it was already burnt at tx conversion on the signer shard. Without the
    // fix the compute is instead mis-charged on the signer shard (which never runs
    // this verify), letting the work escape the receiver shard's budget. See
    // `signature_verification_cost`.
    if apply_state.config.wasm_config.fix_ml_dsa_cost_charging {
        let verify_compute = delegate_signature_verification_compute(
            &apply_state.config.fees,
            signed_delegate_action.delegate_action().public_key(),
        );
        result.compute_usage = safe_add_compute(result.compute_usage, verify_compute)?;
    }
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

    validate_delegate_action_key(state_update, apply_state, delegate_action, result)?;
```

**File:** tools/mirror/src/genesis.rs (L50-59)
```rust
            let resign = |action: DelegateAction, key: SecretKey| {
                let tx_hash = action.get_nep461_hash();
                let signature = key.sign(tx_hash.as_ref());
                Action::Delegate(Box::new(SignedDelegateAction {
                    delegate_action: action,
                    signature,
                }))
            };
            map_delegate_action((&delegate.delegate_action).into(), secret, default_key, resign)
        }
```

**File:** tools/mirror/src/genesis.rs (L60-92)
```rust
        Action::DelegateV2(delegate) => {
            if !delegate_allowed {
                // This should not happen, but we handle the case here defensively
                tracing::warn!(target: "mirror", ?delegate, "a delegate action was contained inside another delegate action");
                return None;
            }
            let versioned_nonce =
                VersionedDelegateActionRef::from(&delegate.delegate_action).nonce();
            let resign = move |action: DelegateAction, key: SecretKey| {
                let signer = InMemorySigner::from_secret_key(action.sender_id.clone(), key);
                let DelegateAction {
                    sender_id,
                    receiver_id,
                    actions,
                    nonce: _,
                    max_block_height,
                    public_key,
                } = action;
                let delegate_action = DelegateActionV2 {
                    sender_id,
                    receiver_id,
                    actions,
                    nonce: versioned_nonce,
                    max_block_height,
                    public_key,
                };
                Action::DelegateV2(Box::new(VersionedSignedDelegateAction::sign(
                    &signer,
                    delegate_action.into(),
                )))
            };
            map_delegate_action((&delegate.delegate_action).into(), secret, default_key, resign)
        }
```
