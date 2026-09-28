### Title
Caller-supplied swap route can inject a wallet-draining `token.transfer` into the victim's signed auth tree, hiding the permission grant inside a routine collateral/debt swap - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The controller accepts a fully caller-supplied `swap: Bytes` route in `swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral`, and forwards it verbatim to the configured swap aggregator (`swap_tokens`, contracts/controller/src/strategies/swap.rs:13-55). Route venues are not allowlisted, so a malicious route can point a hop at an attacker-deployed contract that executes `token.transfer(victim, attacker, amount)` on any token the victim holds. On Soroban, that nested `require_auth(victim)` is satisfied by attaching to the victim's existing authorization tree for the root controller call — the same tree simulation produces and the wallet asks the user to sign. This mirrors CVE-2024-7529: a benign-looking action (a collateral swap) obscures an unrelated permission grant (a full wallet-token transfer), and the victim "grants" it by signing what looks like an ordinary swap.

### Finding Description
- `swap_collateral(caller, account_id, current, amount, new, swap)` and siblings pass attacker-constructed `swap` bytes to `router.execute_strategy` inside `with_flash_guard` (contracts/controller/src/strategies/swap.rs:34-38). The controller only authorizes one exact `transfer(controller → router, amount_in)` on its own behalf via `authorize_transfer_as_current` (common/src/token.rs:36-52); it does not constrain what the router's venue calls do with respect to the *caller's* auth.
- The route's pool/venue addresses come from the caller-supplied `assets` registry (skills/xoxno-swap-aggregator/payload.md), so a route can invoke an arbitrary contract address as a "pool".
- That contract can call `token.transfer(victim_address, attacker_address, victim_balance)` on any Stellar asset contract. The token's `from.require_auth()` is satisfied by the victim's authorization entry for the whole transaction — in recording mode (simulation) the stolen transfer is attached as a sub-invocation under the victim's `swap_collateral` root entry.
- The repo's own test proves both halves: `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` shows the rogue pool's wallet transfer recorded inside the caller's `swap_collateral` auth entry (tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs:194-227), and `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` shows that once the (simulation-produced) tree is signed, the theft executes and Alice's unrelated wallet token is fully drained (same file, 229-269).
- A wallet signing UI shows the root invocation (`swap_collateral` on the controller) prominently; the extra nested `transfer` leaf is buried in the auth tree — the exact "partially obscured security prompt" shape of the CVE.

### Impact Explanation
Theft of user funds. Any token balance in the victim's wallet — including assets the protocol never listed — can be transferred to the attacker in the same transaction the victim believes is a simple collateral/debt swap. The signed tree legitimately authorizes it, so there is no on-chain rejection; the exchange itself can even be made "fair" so nothing looks anomalous.

### Likelihood Explanation
Medium. Exploitation requires the victim to submit an attacker-crafted `swap` payload (e.g., via a malicious frontend, injected quote, or social engineering) and to sign the simulated auth tree without auditing nested sub-invocations. This is a UI-interaction-gated path (like the CVE's `UI:R`), but wallet display of deep auth trees is widely recognized as weak, and the protocol places no allowlist, venue whitelist, or auth-shape bound on routes.

### Recommendation
- Restrict `execute_strategy` venue dispatch to validated/registered pool addresses (a venue allowlist or pool-address verification via `get_tokens`/`token0`/`token1` before the call), so route bytes cannot name arbitrary contracts.
- Alternatively, have the controller bound the caller-facing auth surface: document and enforce that all strategy calls execute under `caller.require_auth()` for the controller only, and recommend wallets/integrators pin simulation auth trees; consider a design where swap routes resolve venues from a stored registry rather than caller-supplied addresses.
- At minimum, warn integrators that `swap` bytes are untrusted input capable of adding arbitrary `require_auth(caller)` leaves to the auth tree.

### Proof of Concept
The repository already contains a working PoC. `Scene::route_through_pool_stealing` builds a `RoutedSwap` whose `hop_pool` is `RogueHopPool`, constructed with `(victim = alice, wallet_token, to = attacker, amount = WALLET_BALANCE)` (tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs:111-125). `RogueHopPool::swap` calls `token::Client::transfer(&victim, &to, &amount)` (lines 62-71). When Alice calls `controller.swap_collateral(alice, account_id, USDC, 50_000_000_000, ETH, route)`:

1. Recording-mode simulation attaches `wallet_token.transfer(alice → attacker, 77_770_000_000)` as a sub-invocation under Alice's `swap_collateral` auth entry — asserted at lines 206-222, with `wallet(alice) == 0` afterward.
2. Submitting that simulated (poisoned) tree in enforcing mode succeeds: `try_swap_with_signed_tree(&rogue, [stolen_transfer])` passes and `wallet(attacker) == WALLET_BALANCE` (lines 259-268), while the same route with the honest root-only tree reverts with `Unauthorized function call for address` (lines 239-256).

The only honest-tree defense is the user noticing the extra leaf — precisely the obscured-permission grant the CVE class describes.