### Title
Crafted swap route executes attacker-chosen pool code under the caller’s authorization tree to steal wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Medium. Controller swap strategies accept caller-controlled route bytes and forward them to the configured router. The route can name an arbitrary hop pool/venue contract; that contract executes inside the same authorization tree and can request a token transfer from the swap caller. If the signed auth tree is taken from simulation, the malicious transfer is authorized even though it is unrelated to the protocol swap.

### Finding Description
`Controller::swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral` accept a `swap: Bytes` argument supplied by the caller (`contracts/controller/src/lib.rs:225-333`). `process_swap_collateral`/`process_swap_debt` only require an authorized owner/delegate caller, then pass `swap` through `swap_tokens_or_passthrough` (`contracts/controller/src/strategies/swap_collateral.rs:40-65`, `contracts/controller/src/strategies/swap_debt.rs:37-72`).

`swap_tokens` authorizes only the controller→router input transfer, but then calls `router.execute_strategy(&controller, &amount_in, swap)` with the raw bytes (`contracts/controller/src/strategies/swap.rs:24-38`). The router decodes the payload and constructs `SwapHop { pool: assets.get_unchecked(op.idx_a), ... }` with no allowlist (`contracts/swap-aggregator/src/execute/mod.rs:151-166`). Venue adapters then dynamically invoke that payload-named pool, e.g. Soroswap calls `get_reserves` and `swap` on `ctx.hop.pool` (`contracts/swap-aggregator/src/venues/soroswap.rs:55-87`).

Because the invoked pool is arbitrary code, its `swap` implementation can call `token::transfer(victim, attacker, amount)` on an unrelated wallet token. In Soroban recording/simulation mode this unauthorized-looking call is attached as a child invocation beneath the victim’s root `swap_collateral` authorization; if the victim signs the simulated tree, the host accepts it and moves the victim’s funds. The repository’s own threat model and regression test document this exact behavior: the route can put third-party code under the caller authorization and steal wallet funds when the poisoned tree is signed (`docs/explanation/threat-model.md:154-165`, `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs:194-268`).

### Impact Explanation
Theft of user funds. The attacker is not limited to the routed `amount_in`: rogue route code can request transfers of any token the caller owns and that the caller’s signed authorization tree permits. The protocol settlement checks—positive measured output and final account risk—still pass, because the stolen asset need not be part of the swap and a fair output can still be paid.

### Likelihood Explanation
A single unprivileged user can reach the path by calling `swap_collateral`/`swap_debt`/`multiply`/`repay_debt_with_collateral` with a crafted route. Exploitation requires the victim to sign an authorization tree containing the extra token transfer, which is the normal failure mode when wallets/clients blindly sign the auth tree produced by simulation for a supplied route. This is not guaranteed for every swap, so Medium rather than High.

### Recommendation
Do not let route bytes select arbitrary executable pool addresses. Restrict venue hops to a verified registry/allowlist of pool contracts for each venue, or make venue adapters verify the pool’s deployed contract identity before `invoke_contract`. Operationally, clients must decode routes and reject any authorization tree with children other than the single expected input-token transfer, but the protocol-side fix is to remove attacker-selected code execution from the swap path.

### Proof of Concept
The in-repo harness `rogue_hop_pool_transfer_joins_caller_auth_tree.rs` implements the exploit:

1. Alice owns an account and holds an unrelated `wallet_token`.
2. The configured router’s `execute_strategy` decodes the route and invokes the route-named `hop_pool` (`UnlistedPoolRouter::execute_strategy`, lines 39-47).
3. The attacker deploys `RogueHopPool` whose `swap` calls `token::transfer(alice, attacker, WALLET_BALANCE)` (lines 56-70).
4. Alice calls `swap_collateral(alice, account_id, USDC_hub_asset, SWAP_IN_USDC, ETH_hub_asset, route)` where `route` names the rogue pool.
5. Simulation records the rogue `transfer` as a child under Alice’s `swap_collateral` root (lines 206-222).
6. With an honest root-only tree the transfer is rejected; with the simulated poisoned tree it succeeds and Alice’s wallet token balance moves to the attacker while the ETH output still settles (lines 239-268).