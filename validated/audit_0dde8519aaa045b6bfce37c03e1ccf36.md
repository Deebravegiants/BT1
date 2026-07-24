### Title
Partial Token Registration State Enables Permanently Lost `fin_transfer` During Deployment Window — (File: near/omni-bridge/src/lib.rs)

### Summary
`deploy_token_internal` registers a token in all bridge maps and marks it as a deployed bridge token **before** the actual NEAR token contract is deployed. During the async window between that registration and the completion of `deploy_token_by_deployer_callback`, a permissionless `fin_transfer` call for that token will mark the transfer as permanently finalized but fail to mint tokens, irreversibly destroying user funds.

### Finding Description

**Bug class (from external report):** State machine — partial state setup that enables unintended actions between setup transactions.

**Root cause — step 1: premature registration**

`deploy_token_internal` (lines 2418–2458) performs all bridge-state writes synchronously before the token contract exists: [1](#0-0) 

`add_token` populates `token_id_to_address`, `token_address_to_id`, and `token_decimals`. `deployed_tokens` and `deployed_tokens_v2` are also set. Only after all of this does the function issue the async deployer call: [2](#0-1) 

Between that outgoing call and the execution of `deploy_token_by_deployer_callback`, the token is fully registered as a deployed bridge token but the NEAR token contract does not yet exist (and the bridge has no storage registered on it).

**Root cause — step 2: `fin_transfer_send_tokens_callback` ignores mint failure**

`fin_transfer` is permissionless — any caller with a valid source-chain proof can invoke it. `fin_transfer_callback` (lines 704–750) finds the token registered, finds its decimals, marks the transfer finalized via `add_fin_transfer`, and calls `process_fin_transfer_to_near`, which calls `send_tokens` → `mint`: [3](#0-2) 

The callback `fin_transfer_send_tokens_callback` carries **no** `#[callback_result]` annotation and therefore never receives the promise result of `send_tokens`: [4](#0-3) 

It only calls `is_refund_required(is_ft_transfer_call)`. For the `mint` path (deployed token, empty `msg`), `is_ft_transfer_call = false`, so `is_refund_required` unconditionally returns `false` without inspecting the promise result: [5](#0-4) 

When `mint` fails because the token contract does not yet exist, the callback still takes the "success" branch: it emits `FinTransferEvent`, sends fees, and leaves the nonce permanently consumed in `finalised_transfers`. The transfer cannot be retried.

**Cleanup in `deploy_token_by_deployer_callback` does not help**

If the deployer call fails, the callback removes the token from all maps: [6](#0-5) 

But this cleanup runs *after* `fin_transfer` has already been processed and the nonce consumed. Even when the deployer succeeds, the bridge has no storage registered on the token until `deploy_token_by_deployer_callback` completes its own `storage_deposit` call, so `mint` still fails during the window.

### Impact Explanation

**Critical — Irreversible fund lock.** The destination nonce is permanently consumed in `finalised_transfers`. No tokens are minted to the recipient. The user's tokens on the source chain are already locked or burned. The transfer cannot be retried because the nonce is marked used. This matches the allowed impact: *Irreversible fund lock, frozen redemption path, or permanently unclaimable user or protocol value.*

### Likelihood Explanation

**Medium.** The window spans two NEAR receipts (the deployer call and its callback). In practice a relayer may submit `deploy_token` and `fin_transfer` in the same block or adjacent blocks. The attacker requires only a valid source-chain proof of an `InitTransfer` event — a proof that is publicly available to any user who initiated a transfer on the source chain. No privileged access is required; `fin_transfer` is fully permissionless.

### Recommendation

1. **Check the `send_tokens` result in `fin_transfer_send_tokens_callback`.** Add a `#[callback_result]` parameter and revert the finalization (remove from `finalised_transfers`, revert lock actions) if the mint/transfer failed, regardless of whether it was a `ft_transfer_call` or a plain `mint`.

2. **Guard `fin_transfer` against partially-deployed tokens.** Before proceeding in `fin_transfer_callback`, verify that the token contract is fully operational (e.g., that the bridge has a non-zero storage balance on the token).

3. **Defer bridge-state registration until deployment is confirmed.** Move `add_token`, `deployed_tokens.insert`, and `deployed_tokens_v2.insert` into `deploy_token_by_deployer_callback` (success branch) rather than in `deploy_token_internal`, so the token is never visible to `fin_transfer` until it is fully deployed.

### Proof of Concept

1. Token X exists on EVM but has not yet been deployed on NEAR.
2. User initiates a transfer of Token X from EVM to NEAR; the EVM bridge emits `InitTransfer`.
3. Relayer calls `deploy_token` on NEAR with a valid `LogMetadata` proof.
4. `deploy_token_callback` → `deploy_token_internal` registers Token X in all bridge maps and issues the async deployer call. Token X is now visible as a deployed bridge token.
5. Before `deploy_token_by_deployer_callback` executes, the user (or any observer with the proof) calls `fin_transfer` with the `InitTransfer` proof.
6. `fin_transfer_callback` finds Token X registered, finds its decimals, marks the transfer finalized (`finalised_transfers.insert`), and calls `send_tokens` → `mint`.
7. `mint` fails: the token contract does not exist (or the bridge has no storage on it).
8. `fin_transfer_send_tokens_callback` runs with `is_ft_transfer_call = false`; `is_refund_required` returns `false`; the callback takes the success branch and emits `FinTransferEvent`.
9. The destination nonce is permanently consumed. No tokens are minted. The user's source-chain tokens are locked/burned. Funds are irreversibly lost.

### Citations

**File:** near/omni-bridge/src/lib.rs (L1193-1201)
```rust
        } else {
            self.deployed_tokens.remove(&token_id);
            self.deployed_tokens_v2.remove(&token_id);
            self.token_id_to_address
                .remove(&(token_address.get_chain(), token_id));
            self.token_address_to_id.remove(token_address);
            self.token_decimals.remove(token_address);
            PromiseOrValue::Value(())
        }
```

**File:** near/omni-bridge/src/lib.rs (L1697-1710)
```rust
    pub fn fin_transfer_send_tokens_callback(
        &mut self,
        #[serializer(borsh)] transfer_message: TransferMessage,
        #[serializer(borsh)] fee_recipient: &AccountId,
        #[serializer(borsh)] is_ft_transfer_call: bool,
        #[serializer(borsh)] storage_owner: &AccountId,
        #[serializer(borsh)] lock_actions: Vec<LockAction>,
    ) {
        let token = self.get_token_id(&transfer_message.token);

        if Self::is_refund_required(is_ft_transfer_call) {
            self.burn_tokens_if_needed(
                token.clone(),
                U128(
```

**File:** near/omni-bridge/src/lib.rs (L1789-1809)
```rust
    fn is_refund_required(is_ft_transfer_call: bool) -> bool {
        if is_ft_transfer_call {
            match env::promise_result_checked(0, MAX_FT_TRANSFER_CALL_RESULT) {
                Ok(value) => {
                    if let Ok(amount) = near_sdk::serde_json::from_slice::<U128>(&value) {
                        // Normal case: refund if the used token amount is zero
                        // The amount can be zero if the `ft_on_transfer` in the receiver contract returns an amount instead of `0`, or if it panics.
                        amount.0 == 0
                    } else {
                        // Unexpected case: don't refund
                        false
                    }
                }
                // Unexpected case: don't refund
                Err(_) => false,
            }
        } else {
            // Not ft_transfer_call: don't refund
            false
        }
    }
```

**File:** near/omni-bridge/src/lib.rs (L1962-1982)
```rust
        self.send_tokens(
            token.clone(),
            recipient,
            U128(
                transfer_message
                    .amount_without_fee()
                    .near_expect(BridgeError::InvalidFee),
            ),
            &msg,
        )
        .then(
            Self::ext(env::current_account_id())
                .with_static_gas(SEND_TOKENS_CALLBACK_GAS)
                .fin_transfer_send_tokens_callback(
                    transfer_message,
                    &fee_recipient,
                    !msg.is_empty(),
                    predecessor_account_id,
                    lock_actions,
                ),
        )
```

**File:** near/omni-bridge/src/lib.rs (L2418-2431)
```rust
        let storage_usage = env::storage_usage();
        self.add_token(
            &token_id,
            token_address,
            metadata.decimals,
            metadata.decimals,
        );

        require!(
            self.deployed_tokens.insert(&token_id),
            BridgeError::TokenExists.as_ref()
        );
        self.deployed_tokens_v2
            .insert(&token_id, &token_address.get_chain());
```

**File:** near/omni-bridge/src/lib.rs (L2451-2458)
```rust
        ext_deployer::ext(deployer)
            .with_static_gas(DEPLOY_TOKEN_GAS)
            .with_attached_deposit(attached_deposit.saturating_sub(required_deposit))
            .deploy_token(token_id.clone(), metadata)
            .then(
                Self::ext(env::current_account_id())
                    .deploy_token_by_deployer_callback(token_address, token_id),
            )
```
