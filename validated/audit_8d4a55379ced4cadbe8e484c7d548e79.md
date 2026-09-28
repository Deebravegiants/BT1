### Title
Attacker-controlled swap routes can inject unauthorized token transfers into the caller’s authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The controller forwards caller-supplied opaque route bytes to the configured swap router after registering only one exact controller-to-router transfer authorization. [1](#0-0)  Because the router resolves pool addresses from the payload and dispatches them without a venue allowlist, route-controlled contract code runs beneath the original caller authorization. [2](#0-1) [3](#0-2)  If transaction simulation records an unexpected `require_auth` invocation by that code and the user signs the resulting authorization tree, the route can transfer unrelated tokens from the user’s wallet. [4](#0-3) 

### Finding Description
The vulnerable entrypoint is `swap_collateral(caller, account_id, current, amount, new, swap)`, where `swap` is caller-controlled `Bytes`. [5](#0-4)  The controller authenticates `caller`, verifies account ownership or delegation, withdraws the selected collateral into controller custody, and calls the shared router path. [6](#0-5) 

`swap_tokens` validates only that the route is nonempty and `amount_in` is positive; it does not decode or constrain the route’s venue addresses. [7](#0-6)  It authorizes exactly `token_in.transfer(controller, router, amount_in)` with no nested invocations, then forwards the untouched payload to `router.execute_strategy(controller, amount_in, swap)`. [8](#0-7) [1](#0-0) 

The router decodes the payload’s address registry, constructs each hop’s `pool`, `token_in`, and `token_out` from those addresses, and dispatches the selected venue adapter. [2](#0-1)  The venue dispatch has no check that `hop.pool` is a known Soroswap, Aquarius, Phoenix, Sushi, or Comet deployment; it invokes the adapter selected by the route byte. [3](#0-2) 

A malicious contract that implements the expected venue ABI can therefore execute arbitrary contract code inside the transaction. If that code invokes `victim_token.transfer(victim, attacker, amount)`, Soroban simulation records the call as a sub-invocation under the victim’s original controller authorization; signing that simulated tree makes the transfer valid. [4](#0-3)  The controller’s later input/output checks only constrain the controller’s swap-token balances and do not inspect other invocations performed while the route executes. [9](#0-8) 

### Impact Explanation
This is theft of user funds outside the collateral supplied to the swap. The malicious route can drain any SEP-41 token balance held by the signing account, provided the transfer is included as a child of the signed authorization tree. [4](#0-3) 

The routed input remains bounded by the controller’s exact authorization and balance checks, but the injected wallet transfer is independent of that bounded input and is not bounded by route output, minimum-out, or final health-factor checks. [9](#0-8) [10](#0-9) 

### Likelihood Explanation
An unprivileged attacker can deploy a contract implementing a supported venue ABI and encode its address as the hop pool in the route payload. [2](#0-1)  The attacker must then induce a user to submit that route through `swap_collateral`, `swap_debt`, `multiply`, or `repay_debt_with_collateral` and sign the authorization tree produced by simulation. [11](#0-10) [12](#0-11) 

That user interaction makes exploitation less likely than a purely unilateral theft, but opaque route bytes materially hide the venue contract from ordinary signers. [13](#0-12)  Simulation preserving the malicious invocation in the signature tree is what converts route-controlled code execution into authorization misuse. [4](#0-3) 

### Recommendation
Do not allow payload bytes to name arbitrary venue contracts. Maintain an on-chain governance-approved registry of valid pool/venue addresses, and reject any hop whose `pool` is not registered for its selected venue before invoking the venue adapter. [2](#0-1) 

At the controller boundary, consider replacing opaque route bytes with a decoded route manifest that commits every venue address, or require a route hash/registry identifier whose venues were previously admitted by governance. [14](#0-13)  Wallets and SDK transaction builders should also simulate the composed lending transaction and reject any caller authorization tree containing children other than the expected input-token transfer. [8](#0-7) [15](#0-14) 

### Proof of Concept
1. Deploy `RoguePool`, which implements the selected venue’s expected swap ABI and additionally executes `token::Client::new(victim_token).transfer(victim, attacker, victim_balance)`. [16](#0-15) 
2. Encode a valid route whose address registry contains the normal `token_in`, normal `token_out`, and `RoguePool` as a hop pool; encode a supported swap opcode and ordinary positive `min_out`. [17](#0-16) 
3. Prefund `RoguePool` with enough `token_out` and implement the venue call so the router observes the required input spend and positive output delta. [18](#0-17) 
4. Have the victim invoke `swap_collateral(victim, account_id, current, amount, new, malicious_swap_bytes)` on an account they own or delegate. [5](#0-4) 
5. The controller withdraws `current` collateral, authorizes only `token_in.transfer(controller, router, amount)`, and invokes `execute_strategy` with the malicious payload. [19](#0-18) 
6. During execution, the router resolves `RoguePool` from the payload and calls it through the selected venue adapter. [2](#0-1) 
7. `RoguePool` performs the hidden `victim_token.transfer(victim, attacker, victim_balance)` call; transaction simulation records it as a sub-invocation under the victim’s `swap_collateral` authorization. [4](#0-3) 
8. If the victim signs that simulated authorization tree, the wallet-token transfer succeeds while the swap can still return positive measured output and pass the controller’s final settlement checks. [9](#0-8)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L21-38)
```rust
    require_positive_amount(env, amount_in);
    assert_with_error!(env, !swap.is_empty(), GenericError::InvalidPayments);

    let controller = env.current_contract_address();
    let router_addr = storage::get_swap_aggregator(env);
    let router = SwapAggregatorClient::new(env, &router_addr);
    let token_in_client = token::Client::new(env, token_in);

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

**File:** contracts/controller/src/lib.rs (L283-301)
```rust
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
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-64)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
    // Check the destination before withdrawing existing collateral.
    require_can_supply(env, &mut cache, account.spoke_id, new);

    let extra_assets = vec![env, current.asset.clone(), new.asset.clone()];
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

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
```

**File:** common/src/token.rs (L43-51)
```rust
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

**File:** contracts/controller/src/strategies/swap_debt.rs (L65-72)
```rust
    let repay_amount = swap_tokens_or_passthrough(
        env,
        caller,
        &new_debt.asset,
        amount_received,
        &existing_debt.asset,
        swap,
    );
```

**File:** contracts/swap-aggregator/src/lib.rs (L245-254)
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
```

**File:** contracts/swap-aggregator/src/program.rs (L183-233)
```rust
    pub(crate) fn decode(env: &Env, ops: &Bytes, assets_len: u32, amounts_len: u32) -> Self {
        if assets_len == 0 || assets_len > MAX_ASSETS || amounts_len > MAX_AMOUNTS {
            panic_with_error!(env, Error::InvalidRouteXdr);
        }

        let len = ops.len();
        if len < HEADER_LEN || len as usize > MAX_PROGRAM_BYTES {
            panic_with_error!(env, Error::InvalidRouteXdr);
        }

        let mut buf = [0u8; MAX_PROGRAM_BYTES];
        ops.copy_into_slice(&mut buf[..len as usize]);

        if buf[head::VERSION] != VERSION {
            panic_with_error!(env, Error::InvalidRouteXdr);
        }

        let op_count = buf[head::OP_COUNT] as u32;
        let weight_count = buf[head::WEIGHT_COUNT] as u32;
        if op_count == 0 || op_count > MAX_OPS || weight_count > MAX_WEIGHTS {
            panic_with_error!(env, Error::EmptyBatch);
        }
        let weights_at = HEADER_LEN + OP_LEN * op_count;
        if len != weights_at + WEIGHT_LEN * weight_count {
            panic_with_error!(env, Error::InvalidRouteXdr);
        }

        let token_in = buf[head::TOKEN_IN] as u32;
        let token_out = buf[head::TOKEN_OUT] as u32;
        let min_out = buf[head::MIN_OUT] as u32;
        if token_in >= assets_len || token_out >= assets_len || min_out >= amounts_len {
            panic_with_error!(env, Error::InvalidRouteXdr);
        }
        if token_in == token_out {
            panic_with_error!(env, Error::SameToken);
        }

        let referral = &buf[head::REFERRAL..head::REFERRAL + 4];
        let referral_id =
            u32::from_be_bytes([referral[0], referral[1], referral[2], referral[3]]) as u64;

        let program = Self {
            buf,
            op_count,
            weights_at,
            token_in,
            token_out,
            min_out,
            referral_id,
        };
        program.validate(env, assets_len, amounts_len, weight_count);
```
