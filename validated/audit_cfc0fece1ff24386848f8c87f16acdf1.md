### Title
Route-nested contract code under the caller's `require_auth` tree can silently drain the signer's wallet — swap strategies execute attacker-named hop contracts that attach unauthorized `token.transfer` calls to the signed authorization tree — (File: contracts/controller/src/strategies/swap.rs)

### Summary
The `cross-env.js` class — a malicious payload smuggled inside a legitimate-looking execution path that exfiltrates everything reachable — maps onto XOXNO Lending's swap-strategy authorization model. `controller::swap_collateral`, `controller::swap_debt`, `controller::multiply`, `controller::flash_position`, and `controller::repay_debt_with_collateral` all funnel a caller-supplied `StrategySwap` byte blob into `router.execute_strategy`, and the route's hop contracts run *below the caller's* `require_auth` root. A route that names an attacker-deployed contract lets that contract issue `token.transfer(victim, attacker, full_balance)` on any token in the victim's wallet; the host records it as a child of the caller's authorization entry, so a victim who signs the simulated tree authorizes the theft of funds that have nothing to do with the position or the routed amount.

### Finding Description
The controller authorizes only its own exact input transfer via invoker-contract auth (`authorize_transfer_as_current`), then invokes the router under the flash guard, and validates only the controller's measured input/output deltas (`RouterOverspend`, `NoSwapOutput`) — `contracts/controller/src/strategies/swap.rs:13-55`. No bound is placed on what else the route does under the caller's auth entry. Because `caller.require_auth()` is taken once at the strategy root and the route bytes select which pool/token addresses are invoked, arbitrary third-party code ends up inside the subtree the caller signs.

The harness proves the mechanism end-to-end in `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:

- `RogueHopPool::swap` calls `token::Client::transfer(&victim, &to, &amount)` on a wallet token the protocol never listed (lines 62-71).
- Simulation records the rogue transfer as a `sub_invocation` of the victim's `swap_collateral` auth entry, and `swap_collateral` succeeds with the wallet fully drained: `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE` (lines 194-227).
- In enforcing mode, signing the recorded ("poisoned") tree makes the theft execute, while the honest root-only tree is rejected (lines 230-269). The source-account-credentials variant shows the same bind without any entry signature (lines 322-368).

The threat model itself documents that neither the payload `min_out` nor the final health-factor gate bounds this loss — "the loss is then the caller's wallet, not the routed amount" — and that the only mitigation is a client-side rule to reject auth trees with unexpected children (`docs/explanation/threat-model.md:142-165`).

### Impact Explanation
Theft of user funds. Every token in the victim's wallet — including assets never supplied to the protocol and unrelated to the position being managed — can be transferred to the attacker in the same transaction that performs a nominally successful `swap_collateral`/`swap_debt`/`multiply`/`repay_debt_with_collateral`. The swap itself can pay out fairly, so nothing on-chain signals the theft beyond the extra auth child. This is exactly the malware's shape: a payload riding a legitimate call that exfiltrates everything it can reach.

### Likelihood Explanation
The attack requires the victim to submit a route containing the attacker's contract and to sign the simulated authorization tree that includes the rogue transfer — i.e., a poisoned route served through a compromised/malicious quote path or phishing, plus a wallet that signs the tree verbatim (which `simulateTransaction` produces by default, per `skills/xoxno-swap-aggregator/payload.md:109-115`). No privileged access, timing, or economic capital is needed by the attacker; the only mitigation is off-chain client hygiene. Documented-as-known, so Medium.

### Recommendation
- Constrain the authorization surface: perform strategy swaps under the controller's own invoker auth exclusively (the caller's auth entry should cover only the strategy root, never nested token transfers of the caller's wallet assets). Where route-hop pulls of the caller are truly required, pre-declare the allowed `(contract, function, from)` set and check the signed tree server-side or via a wrapper contract.
- At minimum, enumerate the exact expected auth children for each strategy verb and reject any tree containing additional `transfer`/`approve` nodes at signing time, and ship the tree-decoding check as enforced SDK behavior rather than documentation.
- Consider routing hop calls through a fresh per-call vault/executor address so caller-scoped auth cannot reach beneath route-selected code.

### Proof of Concept
Existing, executable: `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`.

1. Alice holds 77,770 units of an unlisted wallet token and supplies USDC collateral; the attacker deploys `RogueHopPool` configured `(victim=alice, token=wallet_token, to=attacker, amount=WALLET_BALANCE)`.
2. Attacker serves a `swap_collateral` route whose hop pool is `RogueHopPool`. Alice calls `controller.swap_collateral(alice, account_id, ..., swap_xdr)`.
3. `simulateTransaction` records `transfer(alice → attacker, WALLET_BALANCE)` as a child of Alice's `swap_collateral` entry; the wallet signs the returned tree.
4. Enforcing-mode execution succeeds: `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`, while Alice's ETH collateral leg completes normally (`supply_balance_raw(ALICE, "ETH") == FAIR_OUT_ETH`).