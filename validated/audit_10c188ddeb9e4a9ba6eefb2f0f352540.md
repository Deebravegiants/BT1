### Title
Unvalidated route pools can inject attacker-chosen calls that steal user wallet tokens - ([File: contracts/swap-aggregator/src/execute/mod.rs](contracts/swap-aggregator/src/execute/mod.rs))

### Summary

`execute_strategy` accepts an attacker-controlled `assets` registry whose entries include both token contracts and venue pool contracts. [1](#0-0)  The program decoder validates that each pool index is in bounds, but does not verify that the indexed address belongs to a legitimate or governance-approved pool. [2](#0-1)  Execution then constructs `SwapHop.pool` directly from that registry entry and dispatches the venue adapter against it. [3](#0-2)  Venue adapters invoke attacker-selected contract code at `hop.pool`, such as Phoenix’s `swap` call. [4](#0-3) 

### Finding Description

The router authenticates `sender`, pulls the declared input token, decodes the supplied program, and executes every instruction in order. [5](#0-4)  The address registry is not limited to tokens: each swap instruction resolves `idx_a` as the pool contract and `idx_b`/`idx_c` as the input and output tokens. [6](#0-5) 

This mirrors the SQL-injection class because attacker-controlled input selects executable code rather than merely supplying data. The router validates the route’s structure and measured token deltas, but not the identity or behavior of the called pool. [7](#0-6) 

A malicious pool can therefore execute arbitrary contract code during the swap. If that code calls an unrelated token’s `transfer` with the victim as `from`, Soroban records that authorization requirement beneath the victim’s signed swap authorization. A client that signs the simulated authorization tree without rejecting unexpected children authorizes both the expected input pull and the malicious transfer.

The same issue is reachable through controller strategies: `swap_tokens` forwards caller-supplied `swap` bytes to the configured router after authorizing only the controller’s input transfer to that router. [8](#0-7)  Because the controller does not inspect pool addresses inside the route, malicious route code remains reachable from `multiply`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral`. [9](#0-8) 

### Impact Explanation

A malicious route can steal arbitrary token balances from the victim’s wallet by inserting an unrelated `token.transfer(victim, attacker, amount)` authorization requirement into the transaction. The malicious pool can still satisfy the router’s measured-input and measured-output checks, so the swap completes normally while the unrelated transfer also executes. [10](#0-9) 

The theft is not limited to the declared `token_in` or `total_in`: the injected call can target any token contract and any amount covered by the victim’s signed authorization tree. This is theft of user funds and qualifies as High severity.

### Likelihood Explanation

An unprivileged attacker can deploy the malicious pool and construct a structurally valid route naming it; no privileged role, leaked key, or protocol upgrade is required. [1](#0-0)  Execution does require a victim to sign an authorization tree containing the extra transfer, so this is a route-supply/signing exploit rather than a unilateral wallet drain.

Likelihood is still material because routes are opaque XDR payloads, venue addresses are user-controlled, and neither the router nor controller enforces a pool allowlist. A malicious quote source, compromised frontend, or phishing flow can provide the payload while preserving a plausible fair output and `min_out`. [11](#0-10) 

### Recommendation

Maintain an on-chain allowlist or registry of approved venue pool contracts and reject any swap instruction whose `idx_a` resolves to an unregistered pool. Apply the check inside `Program::decode` or before `dispatch_hop`, rather than relying on clients to inspect signed authorization trees. [3](#0-2) 

If arbitrary pool addresses must remain supported, isolate the swap in a call path that cannot inherit the end user’s authorization for unrelated `require_auth` calls. At minimum, add a defense-in-depth warning in the ABI and require clients to reject any authorization tree containing calls other than the expected input-token pull.

### Proof of Concept

1. The attacker deploys a contract implementing the selected venue’s `swap` ABI.
2. The malicious `swap` implementation performs `victim_token.transfer(victim, attacker, victim_balance)`, then pulls the routed input and sends enough output token back to the router to satisfy measured settlement.
3. The attacker constructs a `StrategyPayload` whose `assets` registry contains `token_in`, `token_out`, and the malicious pool address.
4. The packed instruction uses a swap opcode, `Mode::All`, `idx_a` pointing to the malicious pool, `idx_b` pointing to `token_in`, and `idx_c` pointing to `token_out`.
5. The victim invokes `Router::execute_strategy(victim, total_in, payload)` or a controller strategy carrying the same swap bytes.
6. During simulation, the malicious token transfer appears as an additional child authorization under the victim’s swap authorization.
7. If the victim signs that tree, the malicious pool’s unrelated token transfer executes alongside a nominally successful swap, draining assets that were never declared as swap inputs. [5](#0-4) [12](#0-11)

### Citations

**File:** contracts/swap-aggregator/src/types.rs (L38-44)
```rust
pub struct StrategyPayload {
    /// Amount registry: min-out, fixed inputs, burn floors, mint min-shares.
    pub amounts: Vec<i128>,
    /// Address registry: tokens, pools, and LP share tokens.
    pub assets: Vec<Address>,
    /// Packed program: header, instruction records, split weights.
    pub ops: Bytes,
```

**File:** contracts/swap-aggregator/src/program.rs (L281-287)
```rust
            if idx_a >= assets_len || idx_b >= assets_len {
                panic_with_error!(env, Error::InvalidRouteXdr);
            }
            match opcode {
                Opcode::Swap(_) => {
                    if idx_c >= assets_len {
                        panic_with_error!(env, Error::InvalidRouteXdr);
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L51-85)
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
    let total_min_out = amounts.get_unchecked(program.min_out);
    if total_min_out <= 0 {
        panic_with_error!(&env, Error::SlippageExceeded);
    }

    let router = env.current_contract_address();
    let mut vault = Vault::new(&env);
    let mut tokens_cache: Map<Address, Vec<Address>> = Map::new(&env);

    // Credit the measured delta, not declared `total_in`: a fee-on-transfer
    // input would otherwise draw the shortfall from the fee reserve.
    let credited_in = transfer_amount_measured(
        &env,
        &input_token,
        &sender,
        &router,
        total_in,
        GenericError::AmountMustBePositive,
    );
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L111-131)
```rust
    for i in 0..program.len() {
        prev = execute_op(
            &ctx,
            &mut vault,
            program.op(&env, i),
            prev,
            &mut tokens_cache,
        );
    }

    if !fee_on_input {
        fees::apply_fees_on_token(&env, &mut vault, &output_token, referral_id);
    }

    let total_out = vault.balance_of(&output_token);
    if total_out < total_min_out {
        panic_with_error!(&env, Error::SlippageExceeded);
    }

    vault.withdraw(&output_token, total_out);
    token::Client::new(&env, &output_token).transfer(&router, &sender, &total_out);
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L153-165)
```rust
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

**File:** contracts/swap-aggregator/src/venues/phoenix.rs (L22-25)
```rust
    ctx.authorize_pool_pull();
    let _: i128 = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L34-40)
```rust
    match hop.venue {
        SwapVenue::Soroswap => soroswap::swap(&ctx),
        SwapVenue::Aquarius => aquarius::swap(&ctx, tokens_cache),
        SwapVenue::Phoenix => phoenix::swap(&ctx),
        SwapVenue::Sushi => sushi::swap(&ctx),
        SwapVenue::CometDex => comet::swap(&ctx),
    };
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

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```
