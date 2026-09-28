### Title
Crafted swap route lets arbitrary venue code steal the signer's unrelated wallet tokens under their own authorization tree - (File: contracts/swap-aggregator/src/program.rs)

### Summary
`Router::execute_strategy` decodes a caller-supplied `StrategyPayload` whose address registry (`assets`) names every pool and token the route will touch. The router keeps no allowlist of pool addresses: `Program::decode`/`validate` only range-check registry indices, then each `Swap` hop calls `env.invoke_contract(&hop.pool, "get_reserves"/"swap", ..)` on whatever address the payload encodes (`contracts/swap-aggregator/src/venues/soroswap.rs:55-87`). Because `sender.require_auth()` opens the sender's authorization tree at the root, a malicious "pool" contract invoked mid-route can call `token.transfer(sender, attacker, amount)` on any token the sender holds. Simulation records that transfer as a child of the sender's own auth entry, and if the user signs the simulated tree (the UI-spoofing step, per CVE-2025-3072's bug class), the theft executes. The router's output-minimum check measures only router balance deltas, so it does not bound this loss — the victim's whole wallet balance of any token is exposed, not just the routed input.

### Finding Description
- `execute_strategy` authenticates `sender` and runs the decoded payload via `execute::run` (`contracts/swap-aggregator/src/lib.rs:250-255`).
- `Program::decode`/`validate` perform purely structural checks (opcode, mode, index bounds, same-token) — no check that `assets[idx_a]` is a legitimate pool or that `assets` entries are known tokens (`contracts/swap-aggregator/src/program.rs:183-314`).
- Venue adapters invoke `hop.pool` and `hop.token_in`/`token_out` directly from the registry; e.g., `soroswap::swap` calls `get_reserves` and `swap` on the payload-supplied pool address (`contracts/swap-aggregator/src/venues/soroswap.rs:55-87`).
- The threat model itself documents the exposure: "a route can put third-party code on the call stack below the caller's authorization … it executes if the caller signs that tree. The loss is then the caller's wallet, not the routed amount" (`docs/explanation/threat-model.md:154-165`), and prescribes only an off-chain client mitigation.
- The harness test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` demonstrates the primitive end-to-end: simulation records a rogue `transfer` under the caller's `swap_collateral`/`execute_strategy` entry, and signing that tree moves the tokens.

### Impact Explanation
Theft of user funds: a single signed `execute_strategy` (or controller `swap_collateral`/`swap_debt`/`multiply` route) can drain the signer's balance of arbitrary tokens, unbounded by `total_in`, `min_out`, or the router's measured-delta checks.

### Likelihood Explanation
Medium. Exploitation requires an unprivileged attacker to get a victim to sign a poisoned route — e.g., via a spoofed/malicious frontend serving a crafted `swap_xdr` — but no privileged role, oracle manipulation, or leaked key is needed. Any contract address qualifies as a hop pool, so the attack surface is always available.

### Recommendation
Enforce route hygiene on-chain where feasible: maintain an allowlist of approved venue pool/token contracts (or at minimum verify pool contracts expose the expected interface before handing them the call), and have the router forbid venue-initiated `require_auth` escalation by scoping what hop code may do. At minimum, harden clients per the threat model — decode `swap_xdr` and reject any recorded auth tree containing children beyond the single expected input `transfer` before presenting it for signature.

### Proof of Concept
See `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`: `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` shows a route whose "pool" contract transfers the caller's wallet tokens to the attacker, recorded as a child of the caller's auth entry; `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` shows signing that tree executes the theft.