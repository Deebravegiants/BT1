### Title
Unvalidated caller-supplied route executes arbitrary contracts inside the victim's signed auth tree, stealing wallet funds - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
The external report is an OS command injection: attacker-controlled input is passed unsanitized into an execution context that runs with elevated privilege. The structural analog in XOXNO Lending is the controller's strategy swap path: `swap_tokens` forwards the caller-supplied `swap` byte payload verbatim into `SwapAggregatorClient::execute_strategy` while the caller's `require_auth` invocation is still on the call stack. The route payload names arbitrary pool addresses; any contract it names is invoked inside the transaction and any `token.transfer(victim, attacker, amount)` it issues is recorded by the host as a child of the victim's signed authorization for `swap_collateral` (or `multiply`, `swap_debt`, `repay_debt_with_collateral`). This is exactly a test-pinned behavior, not speculation: `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` drains Alice's unrelated wallet token through a rogue pool named by the route.

### Finding Description
`swap_tokens` (contracts/controller/src/strategies/swap.rs:34-38) authorizes one exact input transfer to the configured router (`authorize_transfer_as_current`) and then invokes `router.execute_strategy(&controller, &amount_in, swap)` under `with_flash_guard`, passing the raw `StrategySwap` bytes the caller submitted: [1](#0-0) 

The controller performs no validation of the venue/pool addresses embedded in `swap` — it only measures its own `token_in`/`token_out` balance deltas afterward (`RouterOverspend`, `NoSwapOutput`). Those deltas bound the routed amount, not the caller's wallet. Because the strategy entrypoints (`swap_collateral`, `multiply`, `swap_debt`, `repay_debt_with_collateral`) take the route from the caller and run under the caller's `require_auth`, a malicious pool contract named inside the payload's asset registry can call `token::Client::transfer(&victim, &attacker, &amount)` for any token the victim holds; Soroban auth treats that as a sub-invocation of the victim's signed tree, and simulation records it there, so it executes the moment the victim signs the simulated envelope.

The harness test proves end-to-end theft: a `RogueHopPool` whose `swap` function transfers `WALLET_BALANCE` of an unrelated token from Alice to the attacker succeeds whenever the signed tree contains the rogue child — which is precisely the tree `simulateTransaction` returns (tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs:194-227, 258-269). The threat model confirms the router keeps no allowlist of the addresses its payload names and that neither the payload minimum nor the final risk gate bounds the loss (docs/explanation/threat-model.md:154-165).

### Impact Explanation
Theft of user funds. The attacker steals arbitrary token balances from the victim's wallet — funds entirely outside the routed swap amount — by embedding a rogue "pool" address in a route the victim signs (e.g., delivered via a malicious quote or phishing payload). The stolen amount is unbounded by the swap's `min_out`, the controller's balance-delta checks, or the position's post-swap health factor, all of which pass because the swap itself can return a fair output. The same exposure exists on every user-facing strategy verb that accepts a route.

### Likelihood Explanation
Reachable by any unprivileged address that can get a victim to submit a crafted `swap` payload: the victim signs exactly the authorization tree that transaction simulation produces, and the rogue transfer appears in it as a child of the expected `swap_collateral`/`multiply` entry. Nothing in the signing flow marks that child as anomalous — a wallet or client that does not decode and audit the route's venue addresses will present a normal-looking signature request. The exploit requires no privileged role, no oracle manipulation, and no reentrancy; it requires only that the victim use an attacker-influenced route, which is the standard threat model for aggregator routes built off-chain.

### Recommendation
Do not execute route payloads that invoke arbitrary addresses under the user's authorization. Concretely: validate the payload's venue/pool addresses against a governance-maintained allowlist in the controller before calling `execute_strategy` (or require the router to enforce such an allowlist), and/or isolate the router call from the caller's auth context so venue code cannot attach child invocations to the victim's tree. At minimum, bound the signed tree: reject any simulated authorization tree for strategy entrypoints that contains children other than the single expected input `token.transfer` from the caller to the router/controller.

### Proof of Concept
```rust
// Attacker-deployed "pool" named inside the route's asset registry.
// From tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs
#[contractimpl]
impl RogueHopPool {
    pub fn __constructor(env: Env, victim: Address, token: Address, to: Address, amount: i128) {
        env.storage().instance()
            .set(&symbol_short!("PLAN"), &(victim, token, to, amount));
    }

    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) =
            env.storage().instance().get(&symbol_short!("PLAN")).unwrap();
        if amount > 0 {
            // Executes under the VICTIM's signed auth tree for swap_collateral.
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
    }
}
```

Attack flow (pinned by `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` and `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer`):

1. Victim requests a route for `swap_collateral(USDC -> ETH)`; attacker supplies a payload whose hop pool is `RogueHopPool(victim, wallet_token, attacker, WALLET_BALANCE)`.
2. `simulateTransaction` records the tree: root `controller.swap_collateral(...)` with a child `wallet_token.transfer(victim -> attacker, WALLET_BALANCE)`.
3. Victim signs the simulated envelope; the transfer executes and the swap still returns `FAIR_OUT_ETH`, so all controller balance/risk checks pass.
4. Result: `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE` — funds outside the swap are stolen, unbounded by `min_out` or the post-swap health check.

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```
