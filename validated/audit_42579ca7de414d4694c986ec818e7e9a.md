### Title
Front-Runnable `SignedDelegateAction` Nonce Consumption Griefs Relayers - (File: `runtime/runtime/src/actions.rs`)

### Summary

NEAR Protocol's meta-transaction (`DelegateAction`) mechanism is structurally analogous to EIP-2612 `permit()`. A `SignedDelegateAction` is an off-chain user signature that any account can wrap in an outer transaction and submit on-chain. Because `apply_delegate_action` does not bind the outer transaction signer to the inner signed payload, an unprivileged attacker who observes a relayer's pending transaction in the mempool can extract the `SignedDelegateAction`, wrap it in their own outer transaction, and submit it first. This consumes the user's access-key nonce, causing the legitimate relayer's transaction to fail with `DelegateActionInvalidNonce`, burning the relayer's gas with no recourse.

### Finding Description

**Vulnerability class:** Front-runnable external call / nonce-consumption griefing.

**Structural parallel to the report:**

| EIP-2612 `permit()` | NEAR `SignedDelegateAction` |
|---|---|
| User signs approval off-chain | User signs `DelegateAction` off-chain |
| Relayer submits `permit()` on-chain | Relayer wraps it in an outer transaction |
| Attacker extracts `(v,r,s)` from mempool | Attacker extracts `SignedDelegateAction` from mempool |
| Attacker calls `permit()` first, consuming nonce | Attacker wraps same payload in own tx, consuming nonce |
| Victim's `supplyWithPermit()` reverts | Relayer's outer tx fails with `DelegateActionInvalidNonce` |

**Root cause in `apply_delegate_action`:** [1](#0-0) 

The function verifies the inner signature (Alice's) and checks the nonce, but it does **not** verify that the outer transaction signer matches any expected relayer. The `SignedDelegateAction` is valid regardless of who wraps it. [2](#0-1) 

**Nonce is consumed unconditionally** inside `validate_delegate_action_key` once all checks pass: [3](#0-2) 

The `DelegateAction` struct itself contains no field binding it to a specific relayer: [4](#0-3) 

The `SignedDelegateAction` signature covers only the inner payload fields — `sender_id`, `receiver_id`, `actions`, `nonce`, `max_block_height`, `public_key` — not the outer transaction signer: [5](#0-4) 

**Attack path:**

1. Alice signs a `DelegateAction` and sends it off-chain to a relayer.
2. The relayer wraps it in an outer `SignedTransaction` and broadcasts it to the network.
3. The attacker observes the pending transaction in the mempool, extracts the `SignedDelegateAction` bytes.
4. The attacker constructs their own outer `SignedTransaction` (attacker as signer, Alice's account as receiver) containing the identical `SignedDelegateAction`.
5. The attacker's transaction is included first (e.g., by paying higher gas or by being the sequencer on an L2-style setup).
6. Alice's access-key nonce is advanced by the attacker's execution.
7. The legitimate relayer's transaction arrives and fails with `DelegateActionInvalidNonce` — the relayer's gas is burned.

The codebase's own comment acknowledges the relayer bears all costs: [6](#0-5) 

### Impact Explanation

**Corrupted protocol values:**
- **Alice's access-key nonce** (DB entry): advanced by the attacker's transaction, making the signed `DelegateAction` permanently invalid.
- **Relayer's NEAR balance**: decreased by gas fees for the failed outer transaction with no refund of the `EXEC` costs already burned.
- **Receipt**: the inner action receipt is either created by the attacker (not the relayer) or, if the attacker provides insufficient gas, Alice's intended actions never execute while her nonce is still consumed.

The most damaging variant: the attacker submits the `SignedDelegateAction` with the minimum gas required to pass validation but insufficient for the inner actions to succeed. Alice's nonce is consumed, her actions fail, and the relayer's transaction also fails — all in one block.

### Likelihood Explanation

- Any unprivileged account can observe pending transactions via public RPC (`broadcast_tx_async` / mempool queries).
- No cryptographic material needs to be forged; the attacker reuses Alice's valid signature verbatim.
- The outer transaction requires only a funded NEAR account (trivially obtainable).
- On sharded NEAR with a sequencer or any node with mempool visibility, this is straightforward to automate.
- The `DelegateAction` design is explicitly documented as relying on off-chain trust between user and relayer, with no on-chain binding to a specific relayer. [7](#0-6) 

### Recommendation

Optionally include a `relayer_id: Option<AccountId>` field inside `DelegateAction` (covered by Alice's signature). In `apply_delegate_action`, if `relayer_id` is `Some(r)`, assert that the outer receipt's `signer_id` equals `r`. This binds the signed payload to a specific relayer, making extraction and re-submission by a third party produce a signature-verification failure rather than a successful nonce consumption. [4](#0-3) [1](#0-0) 

### Proof of Concept

```
// Attacker observes relayer's pending transaction via RPC:
// GET /tx?hash=<relayer_tx_hash>
// Extract SignedDelegateAction bytes from the transaction's actions list.

// Attacker constructs their own outer transaction:
let attacker_tx = SignedTransaction::from_actions(
    attacker_nonce,
    attacker_account_id,          // outer signer = attacker
    alice_account_id,             // outer receiver = Alice (= delegate sender_id)
    &attacker_signer,
    vec![Action::Delegate(Box::new(extracted_signed_delegate_action))],
    current_block_hash,
);

// Submit via RPC before the legitimate relayer's transaction is included.
// Result:
//   - Alice's nonce is consumed.
//   - Relayer's transaction fails: DelegateActionInvalidNonce.
//   - Relayer loses gas fees with no recourse.
```

The nonce-consumption path is confirmed by the existing test: [8](#0-7)

### Citations

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

**File:** runtime/runtime/src/actions.rs (L471-475)
```rust
    // Note, Relayer prepaid all fees and all things required by actions: attached deposits and attached gas.
    // If something goes wrong, deposit is refunded to the predecessor, this is sender_id/Sender in DelegateAction.
    // Gas is refunded to the signer, this is Relayer.
    // Some contracts refund the deposit. Usually they refund the deposit to the predecessor and this is sender_id/Sender from DelegateAction.
    // Therefore Relayer should verify DelegateAction before submitting it because it spends the attached deposit.
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

**File:** runtime/runtime/src/actions.rs (L1421-1459)
```rust
    #[test]
    fn test_validate_delegate_action_key_update_nonce() {
        let (_, signed_delegate_action) = create_delegate_action_receipt();
        let sender_id = &signed_delegate_action.delegate_action.sender_id;
        let sender_pub_key = &signed_delegate_action.delegate_action.public_key;
        let access_key = AccessKey { nonce: 19000000, permission: AccessKeyPermission::FullAccess };

        let apply_state =
            create_apply_state(signed_delegate_action.delegate_action.max_block_height);
        let mut state_update = setup_account(sender_id, sender_pub_key, &access_key);

        // Everything is ok
        let mut result = ActionResult::default();
        validate_delegate_action_key(
            &mut state_update,
            &apply_state,
            (&signed_delegate_action.delegate_action).into(),
            &mut result,
        )
        .expect("Expect ok");
        assert!(result.result.is_ok(), "Result error: {:?}", result.result);

        // Must fail, Nonce had been updated by previous step.
        result = ActionResult::default();
        validate_delegate_action_key(
            &mut state_update,
            &apply_state,
            (&signed_delegate_action.delegate_action).into(),
            &mut result,
        )
        .expect("Expect ok");
        assert_eq!(
            result.result,
            Err(ActionErrorKind::DelegateActionInvalidNonce {
                delegate_nonce: signed_delegate_action.delegate_action.nonce,
                ak_nonce: signed_delegate_action.delegate_action.nonce,
            }
            .into())
        );
```

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

**File:** docs/architecture/how/meta-tx.md (L56-60)
```markdown
Meta transactions only work with a relayer. This is an application layer
concept, implemented off-chain. Think of it as a server that accepts a
`SignedDelegateAction`, does some checks on them and eventually forwards it
inside a transaction to the blockchain network.

```
