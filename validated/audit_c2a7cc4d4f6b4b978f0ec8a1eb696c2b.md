### Title
Unrestricted "one-yocto subsidy" lets any zero-balance account mint free NEAR on promise transfer/function-call actions - (File: runtime/near-vm-runner/src/wasmtime_runner/logic.rs)

### Summary
`promise_batch_action_transfer` and `promise_batch_action_function_call_weight` contain a "skip deduct" path intended only for deterministic accounts calling contracts like `ft_transfer_call` without seed balance. The guard checks only that the attached amount is exactly 1 yoctoNEAR, the `one_yocto_on_promise` feature is enabled, and the *current* account balance is zero — it never verifies that the calling account is actually a deterministic account. Any ordinary account (including a regular user-controlled contract) that has drained its balance to zero can exploit this to have the 1-yoctoNEAR deposit delivered to a receiver while skipping the balance deduction on the sender, effectively minting tokens out of thin air.

### Finding Description
In `promise_batch_action_function_call_weight` and `promise_batch_action_transfer`, the skip-deduct logic is: [1](#0-0) [2](#0-1) 

When `skip_deduct` is true, `subsidized_amount` is incremented instead of calling `deduct_balance`, so `current_account_balance` is left untouched: [3](#0-2) 

Despite this, the action is still appended to the outgoing receipt via `append_action_transfer`/`append_action_function_call_weight`, meaning the receiver will actually be credited the deposit when the receipt executes. The `subsidized_amount` is only propagated up through `VMOutcome`/`ActionResult` for accounting/metrics purposes: [4](#0-3) 

The comment explicitly states this exemption is meant for "deterministic accounts," but the code enforces no such restriction — it only checks that the caller's current balance is zero, which any account can trivially arrange by spending down its own balance (e.g., via a prior transfer or gas burn) before invoking this host function.

### Impact Explanation
Because the deposit is delivered to the receiver but never actually withdrawn from the sender, each exploitation mints 1 yoctoNEAR of value that did not previously exist, violating the protocol's token-supply conservation invariant. While the per-call gain (1 yoctoNEAR) is far smaller than the gas cost of a function call, the primitive is reachable from any contract, in any receipt, and can be invoked repeatedly (e.g., in a loop appending many promise batch actions in a single function call, or across many independent transactions/receipts over time by continually zeroing out the balance again). This is a genuine unauthorized value-creation bug in transaction/receipt execution, not merely a rounding artifact, matching the "concrete token inflation" impact class.

### Likelihood Explanation
Likelihood is moderate-to-low: exploitation is possible from any unprivileged account with a simple contract, requires no validator or node compromise, and only depends on the account having zero NEAR balance at the time of the call (something a contract can engineer for itself). The economic gain per exploitation is minuscule and dwarfed by gas costs, so a rational attacker gains little unless the primitive can be chained at scale (many cheap receipts across many blocks) to accumulate meaningful inflation, or unless it's used to test/violate accounting invariants (e.g., in state-witness validation or supply-conservation checks) rather than for direct profit.

### Recommendation
Restrict the skip-deduct exemption so it can only apply when the calling account is verified to be a deterministic account (e.g., checked via `AccountType::NearDeterministicAccount`), not merely based on the transient `current_account_balance.is_zero()` condition. The check should be tied to an immutable account property established at account creation, not to a balance value the account itself controls.

### Proof of Concept
Conceptually (exact reproduction requires a nearcore devin/test-environment run to confirm, since this was found via static code review):
1. Deploy a contract account `attacker.near` and reduce its balance to (protocol-minimum-required) zero via transfers/burns.
2. From within a function call executed by `attacker.near`, invoke `promise_batch_action_transfer` (or `promise_batch_action_function_call_weight`) with `amount = 1 yoctoNEAR`, targeting a receiver account.
3. Because `current_account_balance.is_zero()` is true and `amount == 1`, `skip_deduct` is `true`; `deduct_balance` is skipped, but `append_action_transfer` still schedules the transfer to the receiver.
4. Repeat within a loop / across many receipts; each iteration nets the receiver 1 yoctoNEAR without any corresponding deduction from `attacker.near`, incrementing total NEAR in circulation beyond what should be possible outside of protocol-defined issuance.

### Citations

**File:** runtime/near-vm-runner/src/wasmtime_runner/logic.rs (L3295-3310)
```rust
    // Allow attaching exactly 1 yoctoNEAR to a promise function call
    // when the contract has zero balance. This lets deterministic accounts
    // call functions like ft_transfer_call that require an attached deposit
    // without needing to be seeded with balance first.
    let skip_deduct = amount == Balance::from_yoctonear(1)
        && ctx.config.one_yocto_on_promise
        && ctx.result_state.current_account_balance.is_zero();
    if skip_deduct {
        ctx.result_state.subsidized_amount = ctx
            .result_state
            .subsidized_amount
            .checked_add(amount)
            .expect("subsidized_amount overflow");
    } else {
        ctx.result_state.deduct_balance(amount)?;
    }
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/logic.rs (L3350-3376)
```rust
    let amount =
        Balance::from_yoctonear(get_u128(&mut ctx.result_state.gas_counter, memory, amount_ptr)?);

    let (receipt_idx, sir) = promise_idx_to_receipt_idx_with_sir(ctx, promise_idx)?;
    let receiver_id = ctx.ext.get_receipt_receiver(receipt_idx);
    let send_fee = transfer_send_fee(
        &ctx.fees_config,
        sir,
        ctx.config.eth_implicit_accounts,
        receiver_id.get_account_type(),
    );
    let exec_fee = transfer_exec_fee(
        &ctx.fees_config,
        ctx.config.eth_implicit_accounts,
        receiver_id.get_account_type(),
    );
    let burn_cost = send_fee;
    let use_gas = burn_cost.gas.checked_add(exec_fee.gas).ok_or(HostError::IntegerOverflow)?;
    ctx.result_state.gas_counter.pay_action_accumulated(
        burn_cost,
        use_gas,
        ActionCosts::transfer,
    )?;
    ctx.result_state.deduct_balance(amount)?;
    ctx.ext.append_action_transfer(receipt_idx, amount);
    Ok(())
}
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L85-94)
```rust
    /// A helper function to subtract balance on transfer or attached deposit for promises.
    ///
    /// ### Args
    ///
    /// * `amount`: the amount to deduct from the current account balance.
    pub(crate) fn deduct_balance(&mut self, amount: Balance) -> Result<()> {
        self.current_account_balance =
            self.current_account_balance.checked_sub(amount).ok_or(HostError::BalanceExceeded)?;
        Ok(())
    }
```

**File:** runtime/runtime/src/function_call.rs (L221-225)
```rust
        account.set_amount(outcome.balance);
        account.set_storage_usage(outcome.storage_usage);
        result.subsidized_amount =
            safe_add_balance(result.subsidized_amount, outcome.subsidized_amount)?;
        result.result = Ok(outcome.return_data);
```
