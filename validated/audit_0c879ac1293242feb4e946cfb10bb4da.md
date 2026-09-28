### Title
Unvalidated route pool addresses let a crafted strategy pull arbitrary tokens from the caller's wallet under its own authorization - (File: contracts/swap-aggregator/src/venues/mod.rs)

### Summary
The swap router dispatches hops to the `pool` address named in the attacker-craftable `swap_xdr` payload with no allowlist. A malicious pool contract placed on the route executes with the caller's `sender.require_auth()` tree open below it, so it can invoke `token.transfer(caller, attacker, x)` on any token the caller holds. The measured-delta checks only cover the hop's `token_in`/`token_out` pair, so this theft path is unbounded by `min_out`, the residual allowance, or the final account-risk gate.

### Finding Description
`execute_strategy(sender, total_in, swap_xdr)` is permissionless: it decodes a `StrategyPayload` whose `assets` registry supplies arbitrary `pool` addresses, then `dispatch_hop` calls whichever venue adapter the opcode names with `hop.pool` as the callee [1](#0-0) . The router self-authorizes only its own pulls via `authorize_as_current_contract`; nothing constrains what the invoked pool contract does while the caller's authorization is on the stack. The threat model confirms the exposure: "the router calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization... The loss is then the caller's wallet, not the routed amount" [2](#0-1) . The harness test `rogue_hop_pool_transfer_joins_caller_auth_tree.rs` demonstrates a `RogueHopPool` contract that calls `token::Client::transfer(victim, to, amount)` inside its `swap` function and shows the invocation joins the caller's recorded auth tree [3](#0-2) . This is the same bug class as the facefusion advisory: an unnormalized, attacker-supplied identifier (pool address instead of job id) escapes the intended namespace (the jobs directory / the legitimate venue set) and reaches arbitrary resources (filesystem paths / the signer's other token balances).

### Impact Explanation
Theft of user funds up to the victim's full balance of any token. When the transaction is built by simulation (the documented flow: `simulateTransaction` produces the auth tree that `attach_simulated_transaction` copies into the envelope [4](#0-3) ), the rogue child transfer is recorded as a child of the caller's entry, and a client that does not diff the tree signs it. The same payload type reaches the controller through `multiply`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral`, but there the sender is the controller contract itself, so exposure is bounded to controller-held funds; the standalone `execute_strategy` path exposes every swap user's wallet directly.

### Likelihood Explanation
Medium. Exploitation requires the victim to sign a transaction whose authorization tree contains a malicious child entry — an honest simulation records it, so a wallet/SDK that inspects the tree can refuse. However, the protocol's own documentation assigns this check to the client rather than enforcing it on-chain, and users routinely sign simulated auth trees without decoding children. No privileges, leaked keys, or protocol misconfiguration are needed; the attacker only needs a malicious route served to or crafted for a victim.

### Recommendation
Enforce the constraint on-chain rather than in client hygiene: maintain an owner-governed venue/pool allowlist in `contracts/swap-aggregator/src/storage.rs` and reject hops in `dispatch_hop` whose `hop.pool` (or the pool resolved inside Aquarius/Phoenix/Sushi/Comet adapters) is not registered, or constrain each hop to a factory-verified pool set. Alternatively, execute venue calls under a scope that cannot inherit the caller's auth — e.g., have the router pull input into its own custody first (already done via the vault) and drop any mechanism by which pool code could attach child invocations to the sender's entry. At minimum, assert inside the strategy executor that no `token.transfer` naming `sender` as `from` occurred outside the single expected input pull, analogous to the strict spend check already applied to the router's balances.

### Proof of Concept
```rust
// Attacker deploys this "pool" and gets it quoted/embedded in a victim's route.
#[contract]
pub struct RogueHopPool;

#[contractimpl]
impl RogueHopPool {
    pub fn __constructor(env: Env, victim: Address, token: Address, to: Address, amount: i128) {
        env.storage().instance().set(&symbol_short!("PLAN"), &(victim, token, to, amount));
    }
    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) =
            env.storage().instance().get(&symbol_short!("PLAN")).unwrap();
        // Joins the victim's auth tree; executes if the victim signs the simulated tree.
        token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
    }
}
```
1. Victim requests a route (or attacker supplies `swap_xdr`) whose Aquarius/other-venue hop names `RogueHopPool` as `assets[pool_idx]`; the hop is constructed so the honest venue leg still satisfies `min_out` and `amount_in` measured deltas.
2. Simulation records `token.transfer(victim, attacker, WALLET_BALANCE)` as a child of the victim's `execute_strategy` auth entry; a client that signs the produced tree authorizes it.
3. On execution, `dispatch_hop` invokes the rogue pool, the nested transfer drains `WALLET_BALANCE` of an arbitrary (even unlisted) token, while the swap itself completes and returns a normal `total_out`.

The existing harness fixture pins this exact behavior: `RogueHopPool::swap` performs the victim-scoped transfer and the test asserts it attaches to the caller's authorization entry [5](#0-4) .

### Citations

**File:** contracts/swap-aggregator/src/venues/mod.rs (L23-40)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L54-72)
```rust
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

**File:** skills/xoxno-swap-aggregator/payload.md (L109-115)
```markdown
## Authorization model

The only signature is the sender's. `execute_strategy` calls `sender.require_auth()`, and the sender's auth entry must cover the nested `token_in.transfer(sender, router, total_in)`; simulation produces that tree (`transaction.simulated = true` envelopes already carry it — `attach_simulated_transaction` copies the simulator's `auth` into the op — and `simulateTransaction` produces it for a locally built one). Do **not** `transfer` or `approve` tokens to the router beforehand: the router pulls the input itself, and tokens sent ahead of time are not credited.

Every venue call is self-authorized by the router with invoker-contract auth (`venues/auth.rs::authorize_as_current` → `env.authorize_as_current_contract`): Phoenix and Sushi (`HopContext::authorize_pool_pull`) and Aquarius (`aquarius/pool.rs::invoke_pool_swap`) register `token_in.transfer(router, pool, amount_in)` before the pool pulls; Comet registers `token_in.approve(router, pool, amount_in, expiry)`, then `swap_exact_amount_in` with a nested entry for the pool's `transfer_from`, then clears the allowance; Soroswap transfers from the router to the pool directly. None of these appear in the sender's auth tree.

A contract calling the router (the lending controller in `contracts/controller/src/strategies/swap.rs`, or your own) is the `sender`: it runs `authorize_transfer_as_current(token_in, self, router, amount_in)` (`common/src/token.rs`) immediately before `execute_strategy(self, amount_in, swap)` and measures its own balance deltas afterward (`RouterOverspend = 501`, `NoSwapOutput = 502` in `common/src/errors.rs`). Details in [composition.md](composition.md).
```
