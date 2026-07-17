### Title
Attacker Can Front-Run `SignedDelegateAction` to DoS Relayer and Waste Relayer Gas - (File: `runtime/runtime/src/actions.rs`)

### Summary
The NEAR meta-transaction system (NEP-366) allows a user (Alice) to sign a `DelegateAction` off-chain and hand it to a relayer, who wraps it in an outer transaction and submits it on-chain. Because the `SignedDelegateAction` is fully embedded in the outer transaction and visible in the public transaction pool, an unprivileged attacker can extract it, wrap it in their own outer transaction, and race it to chain first. When the attacker's transaction lands first, Alice's access-key nonce is consumed. The legitimate relayer's transaction then fails with `DelegateActionInvalidNonce`, causing the relayer to lose gas with no compensation.

### Finding Description

A `DelegateAction` is a user-signed struct containing `sender_id`, `receiver_id`, `actions`, `nonce`, `max_block_height`, and `public_key`. [1](#0-0) 

It is wrapped in a `SignedDelegateAction` (user's signature over the delegate action hash) and embedded verbatim inside the relayer's outer `SignedTransaction`. [2](#0-1) 

The outer transaction is broadcast to the network and is fully visible in the public transaction pool. Any observer can deserialize it, extract the `SignedDelegateAction`, and re-wrap it in a new outer transaction signed by the attacker (the attacker becomes the outer signer/relayer). The inner `SignedDelegateAction` remains valid because it is signed by Alice and carries its own signature.

When the attacker's outer transaction is included first, `apply_delegate_action` is called: [3](#0-2) 

Inside, `validate_delegate_action_key` reads Alice's current access-key nonce and advances it to the delegate nonce value: [4](#0-3) [5](#0-4) 

When the legitimate relayer's transaction is subsequently processed, the same nonce check fires again. Because `delegate_nonce.nonce() <= current_nonce` is now true (the nonce was already advanced), the result is set to `DelegateActionInvalidNonce` and the relayer's outer transaction fails at the action-execution level. The relayer still pays gas for the outer transaction. [4](#0-3) 

### Impact Explanation

**Corrupted protocol value:** The relayer's NEAR token balance is drained (gas paid for a failed outer transaction) and the `ActionResult.result` is set to `Err(DelegateActionInvalidNonce)`, meaning the relayer's intended meta-transaction execution is permanently denied for that nonce.

The relayer cannot retry with the same `SignedDelegateAction` because the nonce is consumed. Alice must sign a new `DelegateAction` with a fresh nonce. An attacker who continuously monitors the mempool and front-runs every relayer submission can permanently DoS any relayer, making the meta-transaction service unusable while draining the relayer's NEAR balance.

**Impact: Medium** — Relayer gas loss and meta-transaction DoS; Alice's action may still execute (via the attacker's tx), but the relayer is not compensated and its service is disrupted.

### Likelihood Explanation

**Likelihood: Medium** — The `SignedDelegateAction` is fully public once the relayer broadcasts the outer transaction. Any node connected to the NEAR P2P network can observe it. The attacker only needs to submit a competing outer transaction before the relayer's is included in a chunk. This is a straightforward race condition requiring no special privileges — only the ability to submit transactions via the public RPC.

### Recommendation

In `apply_delegate_action`, before failing with `DelegateActionInvalidNonce`, check whether the current access-key nonce already equals the delegate nonce (indicating the action was already successfully executed by someone else) and whether the inner actions' effects are already reflected in state. If the nonce was already advanced to exactly the delegate nonce, treat the result as a no-op rather than a hard failure, so the relayer's outer transaction does not waste gas. Alternatively, relayer implementations should be documented to check the current nonce before submission and handle `DelegateActionInvalidNonce` gracefully by not retrying with the same signed action. [4](#0-3) 

### Proof of Concept

1. Alice signs a `DelegateAction` (e.g., `ft_transfer`) with nonce `N` and sends it off-chain to a relayer.
2. The relayer wraps it in `SignedTransaction { signer: relayer, receiver: alice, actions: [Delegate(signed_delegate_action)] }` and broadcasts it via RPC.
3. The attacker observes the transaction in the mempool, deserializes it, and extracts the `SignedDelegateAction`.
4. The attacker constructs `SignedTransaction { signer: attacker, receiver: alice, actions: [Delegate(same_signed_delegate_action)] }` and submits it with a competitive nonce.
5. The attacker's transaction is included first. `validate_delegate_action_key` advances Alice's access-key nonce from `N-1` to `N`. [5](#0-4) 
6. The relayer's transaction is included next. `validate_delegate_action_key` reads `current_nonce = N`, checks `delegate_nonce.nonce() (= N) <= current_nonce (= N)` → true → sets `result.result = Err(DelegateActionInvalidNonce)`. [4](#0-3) 
7. The relayer's outer transaction is charged gas but the inner actions are not re-executed. The relayer loses NEAR with no compensation.

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

**File:** core/primitives/src/action/delegate.rs (L78-95)
```rust
pub struct SignedDelegateAction {
    pub delegate_action: DelegateAction,
    pub signature: Signature,
}

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

**File:** runtime/runtime/src/actions.rs (L422-453)
```rust
pub(crate) fn apply_delegate_action(
    state_update: &mut TrieUpdate,
    apply_state: &ApplyState,
    action_receipt: &VersionedActionReceipt,
    sender_id: &AccountId,
    signed_delegate_action: VersionedSignedDelegateActionRef<'_>,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
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
    if result.result.is_err() {
        // Validation failed. Need to return Ok() because this is not a runtime error.
        // "result.result" will be return to the User as the action execution result.
        return Ok(());
    }
```

**File:** runtime/runtime/src/actions.rs (L604-611)
```rust
    if delegate_nonce.nonce() <= current_nonce {
        result.result = Err(ActionErrorKind::DelegateActionInvalidNonce {
            delegate_nonce: delegate_nonce.nonce(),
            ak_nonce: current_nonce,
        }
        .into());
        return Ok(());
    }
```

**File:** runtime/runtime/src/actions.rs (L685-699)
```rust
    match nonce_update {
        DelegateNonceUpdate::AccessKey => {
            access_key.nonce = delegate_nonce.nonce();
            set_access_key(state_update, sender_id.clone(), public_key.clone(), &access_key);
        }
        DelegateNonceUpdate::GasKey { nonce_index } => {
            set_gas_key_nonce(
                state_update,
                sender_id.clone(),
                public_key.clone(),
                nonce_index,
                delegate_nonce.nonce(),
            );
        }
    }
```
