### Title
Malicious swap route can hide an unrelated wallet transfer in the caller’s authorization tree - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
Router-based account strategies accept a caller-supplied route and invoke the configured router while the account owner’s root authorization is active. A route-selected venue can request an unrelated token transfer from the caller, which Soroban simulation records as an extra child authorization beneath the strategy call. If a wallet or client presents that poisoned tree as an ordinary swap approval, the user’s signature authorizes both the strategy and the theft of unrelated wallet tokens.

### Finding Description
`swap_collateral`, `multiply`, `swap_debt`, and `repay_debt_with_collateral` all flow through `swap_tokens`/`swap_tokens_or_passthrough`. The controller authorizes only its own exact input transfer to the router, then calls `router.execute_strategy` under the flash guard. [1](#0-0) 

Those protections bound only token movement by the controller address. They do not prevent route-selected venue code from calling `token.transfer(victim, attacker, amount)` while the victim’s authorization for the controller strategy is active. The router’s venue pool/token addresses come from the route payload, and there is no venue allowlist preventing attacker-controlled code from appearing below the authorization root. [2](#0-1) 

A successful malicious venue must still make the swap settle: it can pay the required output itself so that measured output and final account checks pass. [3](#0-2) 

### Impact Explanation
Theft of user funds. The malicious nested invocation can transfer any spendable token balance explicitly included in the signed authorization tree, not merely the collateral amount routed through the controller.

The measurable controller checks do not detect the theft because they compare only the controller’s input/output balances and final account risk. [3](#0-2) 

### Likelihood Explanation
An unprivileged attacker can deploy a venue-compatible contract, fund it to return a valid output, and distribute a crafted route or quoting result that reaches `controller::swap_collateral`. Exploitation requires the victim to submit and sign that route and requires the signing interface to inadequately expose the additional child authorization. This user-interaction/UI-scoping requirement matches the medium-severity browser analog.

### Recommendation
Do not place arbitrary route-selected contracts beneath the user’s authorization tree. Constrain swaps to governance-approved pool/venue addresses, or execute external venues under a separate contract-scoped authorization model that cannot request transfers from the account owner.

Until venue trust is enforced, clients must be required to decode the complete Soroban authorization tree and reject any child invocation other than the expected token pull for the selected strategy. This is an integration mitigation, not a contract-level fix.

### Proof of Concept
1. Deploy an attacker contract implementing the pool interface expected by a route venue. Store `(victim, unrelated_token, attacker, victim_balance)`.
2. Fund the venue contract with enough `new.asset` to return a positive, acceptable swap output.
3. Craft a `StrategySwap` whose pool address is the attacker contract and submit `controller::swap_collateral(caller=victim, account_id, current, amount, new, swap)`.
4. During router execution, the malicious venue calls `unrelated_token.transfer(victim, attacker, victim_balance)` and then pays the promised `new.asset` output to the router.
5. Simulation records the unrelated transfer as a child of the victim’s `swap_collateral` authorization. Signing that poisoned tree authorizes the theft while the measured swap output and account finalization checks still pass.

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L29-38)
```rust
    // Snapshot before router execution to measure its spend and output.
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/controller/src/strategies/swap.rs (L40-55)
```rust
    // Reject input gains or overspending; refund only this swap's unused input.
    let in_after = token_in_client.balance(&controller);
    assert_with_error!(env, in_after <= in_before, StrategyError::RouterOverspend);
    let actual_spent = in_before - in_after;
    assert_with_error!(
        env,
        actual_spent <= amount_in,
        StrategyError::RouterOverspend
    );
    let leftover = amount_in - actual_spent;
    if leftover > 0 {
        token_in_client.transfer(&controller, refund_to, &leftover);
    }

    verify_router_output(env, token_out, out_before)
}
```

**File:** docs/explanation/threat-model.md (L154-164)
```markdown
That bound covers the controller's own grant only. The router calls the pool
and token addresses its payload names and keeps no allowlist of them, so a
route can put third-party code on the call stack below the caller's
authorization. A token transfer that such code makes from the caller is
recorded by an honest simulation as a child of the caller's authorization
entry, and it executes if the caller signs that tree. The loss is then the
caller's wallet, not the routed amount, and neither the payload minimum nor the
final risk gate bounds it. An honest swap strategy gives the caller no child
entry, and a direct router swap gives exactly one input transfer. A client must
decode the route it signs and refuse an authorization tree with any other
child. The direct `execute_strategy` path has the same exposure for every swap
```
