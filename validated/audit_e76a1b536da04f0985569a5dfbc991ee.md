## Title
Meta-transaction (`SignedDelegateAction`) griefing/DOS via front-running — relayer identity is not bound to the signed payload - (File: `runtime/runtime/src/actions.rs`, `core/primitives/src/action/delegate.rs`)

### Summary
The reported bug class is a "bearer-signature front-running DOS": a party can observe a valid, still-unconsumed signed authorization in the mempool, extract it, and resubmit it itself before the intended submitter, consuming the nonce and causing the original submission to fail (or redirecting the benefit to the front-runner). Nearcore's NEP-366 meta-transaction (`DelegateAction`/`SignedDelegateAction`) mechanism has the same structural property: the signed payload authorizes execution by *whoever* wraps and submits it, not a specific relayer, and its replay protection is a single account-scoped nonce.

### Finding Description
`SignedDelegateAction::verify()` only checks that the `signature` matches the `DelegateAction` hash and the sender's `public_key` — it does not bind the message to a specific relayer/submitting transaction signer: [1](#0-0) 

When a transaction containing `Action::Delegate(signed_delegate_action)` reaches the sender's shard, `validate_delegate_action_key` validates only the sender's access-key nonce (must be `> current_nonce`) and permission constraints — it performs no check tying the delegate action to a particular relayer account: [2](#0-1) [3](#0-2) 

Because the `SignedDelegateAction` is visible as soon as it appears in any transaction's actions (mempool broadcast, or handed off-chain by the intended relayer's own service to be submitted), any third party can copy the exact `SignedDelegateAction` bytes and wrap them in their own transaction (as the "relayer", i.e., transaction signer), submit it first, and consume the sender's access-key nonce. The originally-intended relayer's transaction, carrying the identical `SignedDelegateAction`, will then fail with `DelegateActionInvalidNonce`, exactly mirroring the ERC-2612 `permit()` front-running DOS pattern where a copied signed payload advances a nonce and invalidates the pending legitimate transaction.

This is explicitly acknowledged as a known trust/design gap in the project's own documentation for the relayer payment flow, where the "payment to relayer" is embedded as an ordinary first action inside the same `DelegateAction` rather than being bound to a specific relayer identity: [4](#0-3) 

### Impact Explanation
Two concrete effects follow directly from the missing relayer binding:
1. **Griefing/DOS of the intended relayer**: The intended relayer's wrapping transaction fails validation (`DelegateActionInvalidNonce`) once the nonce has been consumed by the front-runner's copy, wasting the relayer's transaction-construction effort and potentially any off-chain trust/commitments made to the user.
2. **Value diversion**: If the `DelegateAction`'s actions include a payment to "the relayer" (a common pattern described in the docs, e.g., paying a fungible token fee as the first action), the front-runner — not the intended relayer who did the work of accepting and vetting the request off-chain — collects that payment, since the protocol has no notion of an authorized relayer for a given `DelegateAction`.

This does not cause token inflation or theft from the sender's own state (the sender's intended inner actions still execute correctly and only once), but it enables unauthorized redirection of relayer compensation and denial-of-service against a specific relayer's submission, both are unprivileged-account-reachable effects triggered purely by observing already-signed transaction data.

### Likelihood Explanation
Any user who can see the mempool or otherwise obtain a `SignedDelegateAction` (e.g., a compromised or malicious "second" relayer, or someone monitoring the P2P layer without being a validator) can execute this at low cost — no privileged role or protocol violation is required. The precondition is exactly the same as in the reported ERC20 case: the signed message is fully self-contained and reusable by anyone who has seen it, and the check that consumes it is a simple "nonce greater than stored value" comparison with no relayer binding.

### Recommendation
Bind a `DelegateAction` to its intended relayer, e.g., by adding an optional expected-relayer/`predecessor_id` field to `DelegateAction` that is checked against the transaction's actual signer during `validate_delegate_action_key`, so a copied `SignedDelegateAction` cannot be validly submitted by an unintended party. Alternatively, document/require application-level protections (e.g., short `max_block_height` windows plus off-chain distribution only to a single trusted relayer) as mandatory guidance, since the current mitigation is informal trust only.

### Proof of Concept
1. Alice signs a `DelegateAction` (nonce `N+1`) that includes a first action paying relayer fee in `$FT`, intended for relayer `R1`, and sends it off-chain to `R1`.
2. Attacker `R2` also observes/obtains the same `SignedDelegateAction` bytes (e.g., because `R1` broadcasts it to the mempool, or `R2` is a secondary/backup relayer service Alice also queried).
3. `R2` wraps the identical `SignedDelegateAction` in its own transaction (`R2` as signer/relayer) and submits it with higher gas price/priority so it lands in a chunk first.
4. On Alice's shard, `validate_delegate_action_key` accepts nonce `N+1 > N`, executes the inner actions (including paying the fee to whichever account is coded as recipient — if hardcoded to `R1`'s address the fee still routes correctly, but `R2` paid the gas and "stole" the service; if the fee logic instead pays "the caller"/predecessor, `R2` receives it), and advances the access key nonce to `N+1`.
5. `R1`'s originally prepared transaction, carrying the same `SignedDelegateAction` (nonce `N+1`), is now submitted and rejected with `ActionErrorKind::DelegateActionInvalidNonce` per: [5](#0-4) 
This directly reproduces the DOS/value-diversion pattern described in the source report, substituting NEAR's `DelegateAction` nonce/signature scheme for the ERC-2612 `permit()` nonce/signature scheme.

### Citations

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

**File:** runtime/runtime/src/actions.rs (L558-584)
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
        None => {
            result.result = Err(ActionErrorKind::DelegateActionAccessKeyError(
                InvalidAccessKeyError::AccessKeyNotFound {
                    account_id: sender_id.clone(),
                    public_key: public_key.clone().into(),
                },
            )
            .into());
            return Ok(());
        }
    };
```

**File:** runtime/runtime/src/actions.rs (L630-639)
```rust
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

**File:** docs/architecture/how/meta-tx.md (L66-80)
```markdown
In the example visualized above, the payment is done using \$FT. Together with
the transfer to John, Alice also adds an action to pay 0.1 \$FT to the relayer.
The relayer checks the content of the `SignedDelegateAction` and only processes
it if this payment is included as the first action. In this way, the relayer
will be paid in the same transaction as John.

Note that the payment to the relayer is still not guaranteed. It could be that
Alice does not have sufficient $FT and the transfer fails. To mitigate, the
relayer should check the $FT balance of Alice first.

Unfortunately, this still does not guarantee that the balance will be high
enough once the meta transaction executes. The relayer could waste NEAR gas
without compensation if Alice somehow reduces her \$FT balance in just the right
moment. Some level of trust between the relayer and its user is therefore
required.
```
