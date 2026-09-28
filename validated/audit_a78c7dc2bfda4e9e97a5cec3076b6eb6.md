### Title

Unscoped route contracts can add unrelated wallet transfers to a caller-signed authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary

High. Router-based controller strategies accept caller-controlled `swap` bytes, invoke the configured router, and then validate only the controller's input spend and positive output receipt. [1](#0-0)  Because route hops resolve an arbitrary `pool` address from the payload's asset registry and dispatch venue code against it, a malicious pool can request an unrelated `token.transfer(victim, attacker, amount)` beneath the victim's signed strategy invocation. [2](#0-1) [3](#0-2) 

### Finding Description

`swap_tokens` authorizes only the exact `token_in.transfer(controller, router, amount_in)` invocation needed by the router, but this scopes the controller's contract authority rather than preventing route-selected contracts from adding requests that require the original caller's authority. [4](#0-3) [5](#0-4) 

After execution, the controller only rejects input-balance growth, spending above `amount_in`, and missing `token_out` receipt. [6](#0-5) [7](#0-6) 

The router's `execute_strategy` API takes opaque `swap_xdr`; its program decoder treats `assets[idx_a]` as the hop's pool address without comparing that address to a pool registry or deployment allowlist. [8](#0-7) [9](#0-8) [2](#0-1) 

A Soroswap-labelled hop invokes `get_reserves` and `swap` on that payload-selected address, so an attacker-controlled contract can implement the expected ABI while also requesting a token transfer from the original caller to the attacker. [10](#0-9) [11](#0-10) 

### Impact Explanation

A victim can lose wallet tokens that were never supplied to the lending account and were not part of the intended swap. [6](#0-5) 

The malicious pool can fund the declared output token itself and return a positive output, allowing the router's minimum-output check, the router's exact-spend check, the controller's measured-output check, and the strategy's final account checks all to pass. [12](#0-11) [13](#0-12) [7](#0-6) 

This is theft of user funds rather than poor route pricing: the malicious child transfer can target a different token and recipient while the visible collateral swap still receives economically fair output. [11](#0-10) 

### Likelihood Explanation

The attacker needs to deploy a compatible pool contract and cause the victim to submit the malicious `swap` payload, but no privileged role, leaked key, compromised router, or protocol upgrade is required. [2](#0-1) 

Soroban simulation records the additional caller-authorized token transfer as a child of the strategy authorization; the theft succeeds only if the victim signs that recorded tree. [14](#0-13) 

The likelihood is therefore medium rather than critical: opaque route bytes and a fair-looking output make the poisoned authorization plausible, but the victim's authorization remains a required precondition. [15](#0-14) 

### Recommendation

Constrain route hops to authenticated venue deployments or a governance-maintained pool registry before invoking `pool`-selected code. [2](#0-1) 

For DEX families with deterministic deployments, verify the pool's contract identity or code hash and its registered token pair before calling it. [10](#0-9) 

Treat opaque payload bytes as untrusted executable routing data, and require clients to reject any authorization tree containing calls other than the expected top-level strategy and exact input transfer. [15](#0-14) 

### Proof of Concept

1. Victim has supplied `USDC` collateral to account `account_id` and separately holds `VICTIM_TOKEN` in their wallet. [16](#0-15) 

2. Attacker deploys `FakePool`, funds it with `ETH`, implements `get_reserves() -> (i128, i128)`, and implements `swap(amount_0_out, amount_1_out, to)` so it calls `VICTIM_TOKEN.transfer(victim, attacker, victim_balance)` and transfers the requested `ETH` output to the router. [3](#0-2) 

3. The malicious route uses `assets = [USDC, ETH, FakePool]`, `amounts = [fair_eth_out]`, and one packed `Swap(Soroswap)` operation whose `idx_a`, `idx_b`, and `idx_c` select `FakePool`, `USDC`, and `ETH`, respectively. [17](#0-16) [2](#0-1) 

4. Victim calls `swap_collateral(victim, account_id, usdc_hub_asset, 5_000e7, eth_hub_asset, malicious_swap)`. [18](#0-17) 

5. The controller authorizes the expected `USDC.transfer(controller, router, 5_000e7)`, while `FakePool.swap` causes simulation to record `VICTIM_TOKEN.transfer(victim, attacker, victim_balance)` as another child authorized by the victim. [4](#0-3) [11](#0-10) 

6. After the victim signs the simulated tree, `FakePool` receives the routed `USDC`, steals `VICTIM_TOKEN`, and pays `ETH` back to the router; the router and controller therefore observe exact input spending and a positive `ETH` receipt, and the collateral swap completes. [12](#0-11) [6](#0-5)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L13-20)
```rust
pub(crate) fn swap_tokens(
    env: &Env,
    refund_to: &Address,
    token_in: &Address,
    amount_in: i128,
    token_out: &Address,
    swap: &StrategySwap,
) -> i128 {
```

**File:** contracts/controller/src/strategies/swap.rs (L29-54)
```rust
    // Snapshot before router execution to measure its spend and output.
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });

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

**File:** contracts/controller/src/strategies/swap.rs (L75-83)
```rust
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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L51-66)
```rust
pub(crate) fn run(env: Env, sender: Address, total_in: i128, payload: StrategyPayload) -> i128 {
    sender.require_auth();

    if total_in <= 0 {
        panic_with_error!(&env, Error::InvalidAmount);
    }

    let StrategyPayload {
        amounts,
        assets,
        ops,
    } = payload;
    let program = Program::decode(&env, &ops, assets.len(), amounts.len());

    let input_token = assets.get_unchecked(program.token_in);
    let output_token = assets.get_unchecked(program.token_out);
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L125-133)
```rust
    let total_out = vault.balance_of(&output_token);
    if total_out < total_min_out {
        panic_with_error!(&env, Error::SlippageExceeded);
    }

    vault.withdraw(&output_token, total_out);
    token::Client::new(&env, &output_token).transfer(&router, &sender, &total_out);

    residual::accrue_residual_as_revenue(&env, &mut vault);
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L151-165)
```rust
    match op.opcode {
        Opcode::Swap(venue) => {
            let hop = SwapHop {
                pool: ctx.assets.get_unchecked(op.idx_a),
                token_in: ctx.assets.get_unchecked(op.idx_b),
                token_out: ctx.assets.get_unchecked(op.idx_c),
                venue,
            };
            let amount_in = resolve_amount(ctx, vault, op.mode, &hop.token_in, prev);
            if amount_in <= 0 {
                panic_with_error!(ctx.env, Error::InvalidAmount);
            }

            vault.withdraw(&hop.token_in, amount_in);
            let out = venues::dispatch_hop(ctx.env, ctx.router, &hop, amount_in, tokens_cache);
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L51-87)
```rust
pub(crate) fn swap(ctx: &HopContext<'_>) {
    let token_in_is_0 = ctx.hop.token_in < ctx.hop.token_out;

    let no_args: Vec<Val> = vec![ctx.env];
    let (reserve_0, reserve_1): (i128, i128) = ctx.env.invoke_contract(
        &ctx.hop.pool,
        &Symbol::new(ctx.env, "get_reserves"),
        no_args,
    );
    let (reserve_in, reserve_out) = if token_in_is_0 {
        (reserve_0, reserve_1)
    } else {
        (reserve_1, reserve_0)
    };

    let requested_out = soroswap_amount_out(ctx.env, ctx.amount_in, reserve_in, reserve_out);
    if requested_out <= 0 {
        panic_with_error!(ctx.env, Error::ZeroOutput);
    }

    let token_client = token::Client::new(ctx.env, &ctx.hop.token_in);
    token_client.transfer(ctx.router, &ctx.hop.pool, &ctx.amount_in);

    let (amount_0_out, amount_1_out) = if token_in_is_0 {
        (0_i128, requested_out)
    } else {
        (requested_out, 0_i128)
    };
    let args: Vec<Val> = vec![
        ctx.env,
        amount_0_out.into_val(ctx.env),
        amount_1_out.into_val(ctx.env),
        ctx.router.into_val(ctx.env),
    ];
    let _: () = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
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

**File:** interfaces/swap-aggregator/src/lib.rs (L19-20)
```rust
pub trait SwapAggregatorInterface {
    fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128;
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L42-58)
```rust
    let received = ctx
        .output_balance()
        .checked_sub(before_out)
        .unwrap_or_else(|| panic_with_error!(env, Error::ZeroOutput));
    if received <= 0 {
        panic_with_error!(env, Error::ZeroOutput);
    }

    let after_in = ctx.input_balance();
    let spent = before_in
        .checked_sub(after_in)
        .unwrap_or_else(|| panic_with_error!(env, Error::InvalidAmount));
    if spent != amount_in {
        panic_with_error!(env, Error::InvalidAmount);
    }

    received
```

**File:** contracts/swap-aggregator/src/program.rs (L8-24)
```rust
//! ```text
//! header (10 bytes)
//!   [0]      version, must be VERSION
//!   [1]      token_in   -> assets[..]
//!   [2]      token_out  -> assets[..]
//!   [3]      min_out    -> amounts[..]
//!   [4..8]   referral id, u32 big-endian (0 = none)
//!   [8]      op_count
//!   [9]      weight_count
//! instructions (5 * op_count bytes)
//!   [0]      opcode      -> Opcode
//!   [1]      mode        -> Mode
//!   [2]      idx_a       pool
//!   [3]      idx_b       token_in  | lp share token
//!   [4]      idx_c       token_out | amounts index
//! weights (3 * weight_count bytes)
//!   u24 big-endian parts-per-million, each in 1..=PPM_DENOMINATOR
```

**File:** docs/reference/endpoints.md (L32-35)
```markdown
| `multiply(caller: Address, account_id: u64, spoke_id: u32, collateral: HubAssetKey, debt_to_flash_loan: i128, debt: HubAssetKey, mode: PositionMode, swap: Bytes, initial_payment: Option<(HubAssetKey, i128)>, convert_swap: Option<Bytes>) -> u64` | NFT owner/delegate for existing id | gated | Borrow, swap and supply; optional initial capital. |
| `swap_debt(caller: Address, account_id: u64, existing_debt: HubAssetKey, amount: i128, new_debt: HubAssetKey, swap: Bytes)` | NFT owner/delegate | gated | Borrow new debt, then repay existing debt with the swap output. The new borrow must fit its borrow cap and the borrow-position limit before repayment. |
| `swap_collateral(caller: Address, account_id: u64, current: HubAssetKey, amount: i128, new: HubAssetKey, swap: Bytes)` | NFT owner/delegate | gated | Withdraw, convert and redeposit collateral. |
| `repay_debt_with_collateral(caller: Address, account_id: u64, collateral: HubAssetKey, collateral_amount: i128, debt: HubAssetKey, swap: Bytes, close_position: bool)` | NFT owner/delegate | gated | Direct same-market netting or swap; optional full close. |
```
