### Title
Caller-signed swap routes can authorize unrelated token transfers through unvalidated route code - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Controller strategy entrypoints accept caller-supplied opaque route bytes and execute them through the configured swap aggregator while the caller’s top-level authorization remains active. Because route assets are not limited to listed markets or trusted venues, a malicious route can place attacker-controlled contract code inside the invocation tree and add an unrelated caller-signed token transfer beneath the strategy entrypoint. If the victim signs the auth tree returned by simulation, the routed code can transfer unrelated wallet tokens to an attacker while the controller still observes a valid swap.

### Finding Description
`multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, and `flash_position` all expose caller-provided `swap`/`data` bytes that can direct strategy execution. For routed swaps, `swap_tokens` passes the caller-supplied `StrategySwap` to the configured router without inspecting or constraining the pool/token addresses embedded in the route. [1](#0-0) 

The controller protects only its own balance: it snapshots input and output balances, grants the router one exact controller-token transfer, rejects controller input growth or overspending, and requires positive output. [2](#0-1)  That authorization helper grants no token allowance and creates no controller sub-invocation authority, but it also does not restrict what other calls attacker-selected route code requests from the original caller. [3](#0-2) 

A malicious route can therefore include a “pool” contract that performs a normal-looking swap while also calling `token.transfer(victim, attacker, victim_balance)` on an unrelated token. During transaction simulation, that nested call is recorded as a child of the victim’s authorization for the controller strategy call. If the victim signs the returned tree, Soroban authorizes the unrelated transfer even though it has no relationship to the controller’s `amount_in` grant.

### Impact Explanation
A successful exploit can steal arbitrary caller-held tokens unrelated to the lending swap, subject to what the victim signs in the generated authorization tree. This is theft of user funds and can exceed the routed strategy amount, the collateral being withdrawn, or the debt being converted. The attacker can encode the victim, token, recipient, and amount in the malicious route contract or payload, making the loss up to the victim’s full balance of each targeted token for which a malicious transfer is signed.

### Likelihood Explanation
Exploitation requires user interaction: the attacker must convince a victim to submit a malicious `swap` byte payload and sign the authorization tree containing the hidden transfer. This is realistic for clients that display only the high-level strategy call or expected token input/output rather than fully decoding every nested authorization. The attack does not require protocol privileges, leaked keys, a compromised router owner, or control of an oracle; the attacker only supplies crafted route bytes and attacker-deployed route code.

### Recommendation
Do not allow arbitrary route-selected contract addresses to execute under strategy authorization. Restrict swap routes to an audited venue/pool registry maintained by governance, or constrain the router interface to known venue adapters that cannot make caller-authenticated calls outside the declared swap operations. At a minimum, expose the complete decoded route and all expected authorization children to the signing interface and reject routes containing any caller authorization other than the exact expected input transfer. Preferably redesign settlement so route contracts cannot request authorization from the original caller at all.

### Proof of Concept
1. Alice owns account `A` with supplied USDC and also holds an unrelated token `X` in her wallet.
2. The attacker deploys a malicious “pool” contract storing `(alice, X, attacker, amount)`.
3. The attacker constructs `swap` bytes that route Alice’s USDC through that pool and declare a fair ETH output.
4. Alice submits `swap_collateral(caller=alice, account_id=A, current=usdc_market, amount=amount_in, new=eth_market, swap=malicious_route)`.
5. `process_swap_collateral` withdraws Alice’s collateral to the controller, then `swap_tokens` invokes `router.execute_strategy(controller, amount_in, malicious_route)`. [4](#0-3) 
6. The malicious pool executes `X.transfer(alice, attacker, amount)`. During simulation, this is recorded as a nested authorization beneath Alice’s `swap_collateral` invocation.
7. If Alice signs the poisoned tree, the strategy returns positive ETH output and passes `verify_router_output`, while the unrelated `X` transfer also succeeds. [5](#0-4)

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

**File:** contracts/controller/src/strategies/swap.rs (L40-54)
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
```

**File:** contracts/controller/src/strategies/swap.rs (L74-83)
```rust
/// Returns the output balance increase; rejects zero or negative receipts.
fn verify_router_output(env: &Env, token_out: &Address, balance_before: i128) -> i128 {
    let received = balance_delta_since(
        env,
        token_out,
        &env.current_contract_address(),
        balance_before,
    );
    assert_with_error!(env, received > 0, StrategyError::NoSwapOutput);
    received
```

**File:** common/src/token.rs (L33-51)
```rust
/// Authorizes, on behalf of the current contract, one `transfer(from, to, amount)`
/// call on `token_addr` made deeper in the next contract call (for example by
/// the pool). The entry allows no further sub-invocations.
pub fn authorize_transfer_as_current(
    env: &Env,
    token_addr: &Address,
    from: &Address,
    to: &Address,
    amount: i128,
) {
    let entry = InvokerContractAuthEntry::Contract(SubContractInvocation {
        context: ContractContext {
            contract: token_addr.clone(),
            fn_name: symbol_short!("transfer"),
            args: (from.clone(), to.clone(), amount).into_val(env),
        },
        sub_invocations: Vec::new(env),
    });
    env.authorize_as_current_contract(vec![env, entry]);
```

**File:** contracts/controller/src/lib.rs (L280-302)
```rust
    /// Withdraws `amount` of `current`, converts it to `new` via `swap` and
    /// redeposits the proceeds. Requires owner or delegate authorization.
    #[when_not_paused]
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
    ) {
        strategies::swap_collateral::process_swap_collateral(
            &env,
            &caller,
            SwapCollateralParams {
                account_id,
                current: &current,
                from_amount: amount,
                new: &new,
                swap: &swap,
            },
        );
```
