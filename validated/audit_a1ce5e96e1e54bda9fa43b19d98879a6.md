### Title
Caller-signed swap routes let an attacker-selected pool spend arbitrary wallet tokens - (File: contracts/swap-aggregator/src/execute/mod.rs)

### Summary
`execute_strategy` authenticates the supplied `sender`, then executes a completely caller-selected venue address without constraining that venue's call stack to the authorized input-token movement. A malicious pool contract included in the route can therefore attach an unrelated token transfer to the sender's authorization tree and move funds beyond `total_in`. The router's post-hop balance checks validate only the routed `token_in` and `token_out`; they do not prevent the pool from making other calls under the caller's authorization. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`execute_strategy` performs only a top-level `sender.require_auth()` before decoding and executing the supplied route. [4](#0-3)  Each swap hop takes its `pool`, `token_in`, `token_out`, and venue from the caller-controlled address and instruction registries. [5](#0-4) [6](#0-5)  The dispatcher then directly invokes whichever contract address was supplied as the pool. [7](#0-6) 

For pull-style venues, the router authorizes the pool to transfer exactly `amount_in` of `token_in` from the router. [8](#0-7)  However, no code enforces that the arbitrary pool's invocation remains limited to that nested authorization. The project's threat model documents the resulting failure mode: a route can put third-party code below the caller's authorization and have that code make an unrelated token transfer from the caller; an honest simulation records it in the caller's authorization tree, and the signed tree executes it. [3](#0-2) 

After the pool returns, the dispatcher measures only the router's `token_out` increase and `token_in` decrease. [9](#0-8)  The final route check similarly requires only that the measured output vault balance meets the payload's positive minimum before paying `sender`. [10](#0-9)  A malicious pool can satisfy both checks by holding or minting a positive amount of the declared output token and paying a dust amount to the router, while its callback already stole unrelated assets.

### Impact Explanation
A victim who signs a malicious route can lose unrelated token balances in their wallet, not merely the declared `total_in` or the routed funds. [3](#0-2)  The theft succeeds atomically inside a transaction whose swap result still satisfies the router's measured output and residual checks. [10](#0-9) 

This is theft of user funds. The attacker does not need a privileged role because pool addresses are selected by the caller-supplied route rather than being restricted to an allowlist or verified implementation. [11](#0-10) [2](#0-1) 

### Likelihood Explanation
Any unprivileged user can deploy a malicious Wasm pool and construct a syntactically valid route that invokes it through one of the supported venue adapters. [12](#0-11) [7](#0-6)  Exploitation requires a victim to sign and submit the malicious `swap_xdr`; this is realistic when routes are generated or relayed off-chain, but the user can avoid it by decoding the complete authorization tree and rejecting unexpected child invocations. [13](#0-12)  The contract itself currently leaves that validation to the client. [4](#0-3) 

### Recommendation
Do not execute routes against arbitrary pool addresses. Maintain an authenticated venue/pool registry and invoke only the specific audited pool functions expected by each adapter, or use an authorization model that cannot allow an unrelated caller-token transfer to join the sender's authorization tree. At minimum, reject routes whose pool address is not known to the router, document that signed simulations must be decoded recursively, and abort any transaction whose authorization tree contains a child other than the exact expected input-token movement.

### Proof of Concept
1. Attacker deploys `MaliciousPool` implementing the function used by a supported venue adapter, for example Phoenix's `swap` entrypoint.
2. Attacker prepares a `StrategyPayload` whose `assets` contain:
   - the victim's input token;
   - any output token held by `MaliciousPool`;
   - `MaliciousPool` as the hop's `pool`.
3. The payload's instruction encodes a Phoenix swap with `pool = MaliciousPool`, `token_in = input`, and `token_out = output`; the route's `min_out` amount is `1`.
4. Victim calls:
   ```text
   Router::execute_strategy(
       sender = victim,
       total_in = victim_input_amount,
       swap_xdr = attacker_payload
   )
   ```
5. `execute_strategy` obtains `victim.require_auth()`, pulls `victim_input_amount` into the router, and dispatches the hop. [14](#0-13) 
6. The Phoenix adapter authorizes the pool pull and invokes `MaliciousPool::swap`. [15](#0-14) 
7. Inside `swap`, `MaliciousPool` invokes `unrelated_token.transfer(victim, attacker, victim_balance)`. During honest simulation this invocation is represented in the victim's authorization tree rather than in the router's one-input authorization, so a signature over the tree accepts it. [3](#0-2) 
8. `MaliciousPool` transfers one unit of `output` to the router and consumes the routed input normally.
9. The dispatcher sees positive output and exact input spend, the final minimum-output check passes, and the transaction commits both the dust swap and the unrelated victim-wallet transfer. [9](#0-8) [10](#0-9)

### Citations

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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L152-165)
```rust
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

**File:** contracts/swap-aggregator/src/types.rs (L12-19)
```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SwapVenue {
    Soroswap,
    Aquarius,
    Phoenix,
    Sushi,
    CometDex,
}
```

**File:** contracts/swap-aggregator/src/types.rs (L21-29)
```rust
/// One pool hop: swaps `token_in` for `token_out` through `venue`.
///
/// Built per instruction from registry indices; venue adapters consume this.
#[derive(Clone, Debug)]
pub struct SwapHop {
    pub pool: Address,
    pub token_in: Address,
    pub token_out: Address,
    pub venue: SwapVenue,
```

**File:** contracts/swap-aggregator/src/types.rs (L32-44)
```rust
/// Full strategy decoded from `execute_strategy` XDR.
///
/// Instructions reference `assets` and `amounts` by `u8` index, so an address
/// or amount used by several hops is carried exactly once.
#[contracttype]
#[derive(Clone, Debug)]
pub struct StrategyPayload {
    /// Amount registry: min-out, fixed inputs, burn floors, mint min-shares.
    pub amounts: Vec<i128>,
    /// Address registry: tokens, pools, and LP share tokens.
    pub assets: Vec<Address>,
    /// Packed program: header, instruction records, split weights.
    pub ops: Bytes,
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

**File:** contracts/swap-aggregator/src/venues/mod.rs (L87-96)
```rust
    /// Authorizes the pool to pull `amount_in` of `token_in` from the router.
    pub fn authorize_pool_pull(&self) {
        authorize_token_transfer(
            self.env,
            &self.hop.token_in,
            self.router,
            &self.hop.pool,
            self.amount_in,
        );
    }
```

**File:** contracts/swap-aggregator/src/venues/phoenix.rs (L11-25)
```rust
pub(crate) fn swap(ctx: &HopContext<'_>) {
    let args: Vec<Val> = vec![
        ctx.env,
        ctx.router.into_val(ctx.env),
        ctx.hop.token_in.into_val(ctx.env),
        ctx.amount_in.into_val(ctx.env),
        Option::<i128>::None.into_val(ctx.env),
        Option::<i64>::None.into_val(ctx.env),
        Option::<u64>::None.into_val(ctx.env),
        Option::<i64>::None.into_val(ctx.env),
    ];
    ctx.authorize_pool_pull();
    let _: i128 = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
```
