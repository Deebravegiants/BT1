This confirms the analog: `apply_delegate_action` at [1](#0-0)  validates a `SignedDelegateAction` on the receiver's shard, and `validate_delegate_action_key` performs the nonce check that determines success/failure [2](#0-1) . Since `DelegateAction`/`SignedDelegateAction` carries no binding to a specific relayer identity, and gas/deposit costs for the wrapping transaction are charged to whichever relayer's outer transaction gets included first [3](#0-2) , this is a legitimate structural analog to the permit front-running class of bug.

### Title
Front-runnable `SignedDelegateAction` nonce allows griefing/DOS of relayers submitting NEP-366 meta transactions - (File: `runtime/runtime/src/actions.rs`)

### Summary
A `SignedDelegateAction` (NEP-366 meta transaction), like an ERC-2612 `permit` signature, is a self-contained, one-time-redeemable authorization that is not bound to any specific submitter/relayer. Once a relayer broadcasts the outer `SignedTransaction` wrapping it, the `SignedDelegateAction` bytes are publicly visible before inclusion. Any third party can copy those bytes into their own transaction and get it included first, consuming the sender's access-key/gas-key nonce. This causes the original relayer's transaction to fail on the nonce check, exactly analogous to how permit signatures extracted from the mempool let attackers front-run and grief `depositWithSignature()`/`permit()` callers.

### Finding Description
`DelegateAction`/`SignedDelegateAction` contains `sender_id`, `receiver_id`, `actions`, `nonce`, `max_block_height`, and `public_key`, but no field identifying which relayer is authorized to submit it [4](#0-3) . `SignedDelegateAction::verify()` only checks that the ed25519/NEP-461 signature matches the `delegate_action` payload and `public_key` — it places no restriction on who wraps and submits it in an outer transaction [5](#0-4) .

When the outer transaction is processed, `apply_delegate_action` verifies the signature, expiry, and sender/receiver match, then calls `validate_delegate_action_key`, which loads the sender's access key and enforces `delegate_nonce.nonce() <= current_nonce` → `DelegateActionInvalidNonce` [6](#0-5) . On success, the nonce is persisted immediately [7](#0-6) , meaning whichever transaction carrying that exact `SignedDelegateAction` lands first on-chain "wins" the nonce, and any subsequent submission of the same delegate action fails with `DelegateActionInvalidNonce`, as directly demonstrated by the replay test [8](#0-7) .

Because the relayer (the outer transaction's signer) pays gas and deposit costs for the wrapped delegate action's `SEND`/base transaction costs regardless of whether the delegate action itself later succeeds or fails on the receiver shard [9](#0-8) , an attacker who observes a pending `SignedDelegateAction` in the network/mempool can wrap the *same* signed bytes in their own transaction and get it included first (front-run), consuming the sender's nonce. The original relayer's transaction, when it lands afterward, fails validation with `DelegateActionInvalidNonce`, wasting the gas/fees the relayer already committed to the transaction submission — the classic "front-run a signature-carrying single-use authorization to grief the intended submitter" bug class.

### Impact Explanation
This is a griefing/DOS vector against relayers (a core Medium-severity impact, matching the original report's classification), not a fund-theft vulnerability, because the delegate action's inner `actions` still ultimately execute for the intended sender/receiver (the front-runner cannot redirect fund flows, since `receiver_id`/`actions` are fixed inside the signed payload and re-checked by `apply_delegate_action`'s sender/receiver match [10](#0-9) ). The impact is financial griefing: relayers can be made to pay gas for transactions that revert purely due to nonce collision, undermining the trust model that meta-transaction relayer infrastructure depends on, and this is already acknowledged as a source of relayer risk in the codebase's own design docs discussing nonce-sharing races [11](#0-10) .

### Likelihood Explanation
Likelihood is limited by the requirement that an attacker observe a `SignedDelegateAction` before its wrapping transaction is finalized (e.g., via mempool/gossip visibility or a leaked relayer API request) and then successfully race their own wrapping transaction into an earlier block/shard-processing slot. This requires network-level timing but no privileged access, cryptographic break, or validator collusion — it is analogous in reachability to standard permit front-running, which is why NEAR's own meta-tx documentation already discusses relayer trust assumptions and nonce-sharing races as inherent limitations of the NEP-366 MVP [12](#0-11) .

### Recommendation
Consider binding a `SignedDelegateAction` to a specific authorized relayer (e.g., an optional `relayer_id` field checked against the outer transaction's `signer_id`), or allow the sender to specify a nonce/relayer commitment that only a designated relayer can redeem, so that copying the signed bytes from the network does not let an arbitrary third party consume the sender's nonce ahead of the intended relayer.

### Proof of Concept
1. Alice signs a `DelegateAction` (`nonce = N`) and sends it off-chain to Relayer R, per the documented flow [13](#0-12) .
2. R wraps it in `SignedTransaction` T1 (`Action::Delegate(signed_delegate_action)`) and broadcasts T1.
3. Attacker M observes T1 in the network before finalization, extracts the identical `SignedDelegateAction` bytes, and wraps them into their own transaction T2, paying trivial gas, and gets T2 included first.
4. `apply_delegate_action`/`validate_delegate_action_key` accepts T2, advancing the sender's access-key nonce to `N` [14](#0-13) .
5. T1 (R's transaction) is processed next; `validate_delegate_action_key` now sees `delegate_nonce.nonce() (N) <= current_nonce (N)` and returns `ActionErrorKind::DelegateActionInvalidNonce`, exactly as reproduced by the existing replay test [8](#0-7)  — R has paid gas/fees for a transaction that provides it no benefit, having been front-run.

### Citations

**File:** runtime/runtime/src/actions.rs (L437-461)
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
```

**File:** runtime/runtime/src/actions.rs (L467-474)
```rust
    if delegate_action.sender_id().as_str() != sender_id.as_str() {
        result.result = Err(ActionErrorKind::DelegateActionSenderDoesNotMatchTxReceiver {
            sender_id: delegate_action.sender_id().clone(),
            receiver_id: sender_id.clone(),
        }
        .into());
        return Ok(());
    }
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

**File:** runtime/runtime/src/actions.rs (L712-727)
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

**File:** docs/architecture/how/meta-tx.md (L40-53)
```markdown
With meta transactions, Alice can create a `DelegateAction`, which is very
similar to a transaction. It also contains a list of actions to execute and a
single receiver for those actions. She signs the `DelegateAction` and forwards
it (off-chain) to a relayer. The relayer wraps it in a transaction, of which the
relayer is the signer and therefore pays the gas costs. If the inner actions
have an attached token balance, this is also paid for by the relayer.

On chain, the `SignedDelegateAction` inside the transaction is converted to an
action receipt with the same `SignedDelegateAction` on the relayer's shard. The
receipt is forwarded to the account from `Alice`, which will unpacked the
`SignedDelegateAction` and verify that it is signed by Alice with a valid Nonce
etc. If all checks are successful, a new action receipt with the inner actions
as body is sent to `FT`. There, the `ft_transfer` call finally executes.

```

**File:** docs/architecture/how/meta-tx.md (L121-168)
```markdown
For delegate actions beside each other, there was a bit of back and forth during
the NEP-366 design phase. The potential use case here is essentially the same as
having multiple receivers in a delegate action. Naturally, it runs into all the
same complications (false sense of atomicity) and ends with the same conclusion:
Omitted from the MVP and left open for future improvement.

## Limitation: Accounts must be initialized

Any transaction, including meta transactions, must use NONCEs to avoid replay
attacks. The NONCE must be chosen by Alice and compared to a NONCE stored on
chain. This NONCE is stored on the access key information that gets initialized
when creating an account.

Implicit accounts don't need to be initialized in order to receive NEAR tokens,
or even $FT. This means users could own $FT but no NONCE is stored on chain for
them. This is problematic because we want to enable this exact use case with
meta transactions, but we have no NONCE to create a meta transaction.

For the MVP, the proposed solution, or work-around, is that the relayer will
have to initialize the account of Alice once if it does not exist. Note that
this cannot be done as part of the meta transaction. Instead, it will be a
separate transaction that executes first. Only then can Alice even create a
`SignedDelegateAction` with a valid NONCE.

Once again, some trust is required. If Alice wanted to abuse the relayer's
helpful service, she could ask the relayer to initialize her account.
Afterwards, she does not sign a meta transaction, instead she deletes her
account and cashes in the small token balance reserved for storage. If this
attack is repeated, a significant amount of tokens could be stolen from the
relayer.

One partial solution suggested here was to remove the storage staking cost from
accounts. This means there is no financial incentive for Alice to delete her
account. But it does not solve the problem that the relayer has to pay for the
account creation and Alice can simply refuse to send a meta transaction
afterwards. In particular, anyone creating an account would have financial
incentive to let a relayer create it for them instead of paying out of their own
pockets. This would still be better than Alice stealing tokens but
fundamentally, there still needs to be some trust.

An alternative solution discussed is to do NONCE checks on the relayer's access
key. This prevents replay attacks and allows implicit accounts to be used in
meta transactions without even initializing them. The downside is that meta
transactions share the same NONCE counter(s). That means, a meta transaction
sent by Bob may invalidate a meta transaction signed by Alice that was created
and sent to the relayer at the same time. Multiple access keys by the relayer
and coordination between relayer and user could potentially alleviate this
problem. But for the MVP, nothing along those lines has been approved.
```

**File:** docs/architecture/how/meta-tx.md (L195-214)
```markdown
Ok, now adapt for meta transactions. Let's assume Alice uses a relayer to
execute actions with Bob as the receiver.

1. The relayer purchases the gas for all inner actions, plus the gas for the
   delegate action wrapping them.
2. The cost of sending the inner actions and the delegate action from the
   relayer to Alice's shard will be burned immediately. The condition `relayer
   == Alice` determines which action `SEND` cost is taken (`sir` or `not_sir`).
   Let's call this `SEND(1)`.
3. On Alice's shard, the delegate action is executed, thus the `EXEC` gas cost
   for it is burned. Alice sends the inner actions to Bob's shard. Therefore, we
   burn the `SEND` fee again. This time based on `Alice == Bob` to figure out
   `sir` or `not_sir`. Let's call this `SEND(2)`.
4. On Bob's shard, we execute all inner actions and burn their `EXEC` cost.

Each of these steps should make sense and not be too surprising. But the
consequence is that the implicit costs paid at the relayer's shard are
`SEND(1)` + `SEND(2)` + `EXEC` for all inner actions plus `SEND(1)` + `EXEC` for
the delegate action. This might be surprising but hopefully with this
explanation it makes sense now!
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

**File:** test-loop-tests/src/tests/gas_keys.rs (L274-296)
```rust
    // Replaying the same delegate (same gas key nonce) is rejected.
    let block_hash = get_shared_block_hash(&env.node_datas, &env.test_loop.data);
    let replay_tx = SignedTransaction::from_actions(
        next_relayer_nonce(),
        relayer.clone(),
        sender.clone(),
        &relayer_signer,
        vec![Action::DelegateV2(Box::new(signed_delegate))],
        block_hash,
    );
    let replay_outcome = env.rpc_runner().execute_tx(replay_tx, Duration::seconds(5)).unwrap();
    assert!(
        matches!(
            replay_outcome.status,
            FinalExecutionStatus::Failure(TxExecutionError::ActionError(ActionError {
                kind: ActionErrorKind::DelegateActionInvalidNonce { .. },
                ..
            }))
        ),
        "expected DelegateActionInvalidNonce on replay, got {:?}",
        replay_outcome.status,
    );
}
```
