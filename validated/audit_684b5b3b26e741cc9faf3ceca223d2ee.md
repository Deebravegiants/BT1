### Title
Attacker-crafted `swap` route bytes execute arbitrary contract code under the victim's signed authorization tree, draining wallet tokens unrelated to the swap - (File: contracts/controller/src/strategies/swap.rs)

### Summary
CVE-2023-30130 is "execute arbitrary code via a crafted script in a parameter" (CWE-94). The analog in XOXNO Lending is the opaque `swap`/`steps` `Bytes` parameter accepted by `multiply`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral`. The controller forwards these bytes verbatim to the swap router without decoding or allowlisting the pool/token addresses they name. Because Soroban records every `require_auth` performed during simulation as a child of the signer's authorization entry, a route that names an attacker-deployed "pool" contract can invoke `token.transfer(victim, attacker, X)` *inside* the victim's signed tree — arbitrary code execution smuggled in a user-supplied parameter, exactly the reported bug class.

### Finding Description
`swap_tokens` in `contracts/controller/src/strategies/swap.rs:13-55` is reached by every strategy verb. It:

1. Asserts only that `swap` is non-empty (`swap.rs:22`) — it never parses the payload.
2. Grants the router exactly one `authorize_transfer_as_current` for the swap input (`swap.rs:34`), which bounds the *controller's* exposure but not the caller's.
3. Calls `router.execute_strategy(&controller, &amount_in, swap)` inside the flash guard (`swap.rs:36-38`).

The `swap` bytes are an attacker-controlled serialized program: `StrategySwap`/`swap_xdr` decodes into hop records whose `pool` and `token` fields are arbitrary `Address` values the router invokes (`docs/explanation/threat-model.md:154-165` explicitly documents that the router "keeps no allowlist" of payload-named addresses and that such code "executes if the caller signs that tree").

The trap is the auth-recording semantics: when a user simulates `swap_collateral(caller, account_id, ..., route)`, any `token.transfer(caller, …)` issued by a payload-named contract is recorded as a `sub_invocation` under the caller's `swap_collateral` auth entry. If the caller signs the recorded tree — which a wallet presents as "the transaction you requested" — the enforcing host executes the theft. The in-repo test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs:194-227` demonstrates this end-to-end: a `RogueHopPool` named in the route transfers Alice's entire `WALLET_BALANCE` of an unrelated token to the attacker, while the swap still returns fair output and the account passes all risk gates.

### Impact Explanation
**Theft of user funds.** The stolen amount is unbounded by the swap size, the payload `min_out`, or the controller's final health-factor check — the rogue hop moves tokens from the caller's *wallet*, not the routed input. In the test, Alice loses her full 77,770-unit balance of a token the protocol never listed while receiving a perfectly fair swap output. Any holder of a lending account who signs a malicious route is exposed; the same primitive applies to direct `execute_strategy` callers and to every strategy verb that embeds a route.

### Likelihood Explanation
Route bytes are produced off-chain and passed opaquely, so the attack surface is realized whenever a user accepts a route they did not generate — phishing front-ends, compromised quote services, or a malicious counterparty handing a victim a "ready-to-sign" `swap_collateral`/`multiply` transaction. No privileges, leaked keys, or protocol misconfiguration are needed: the victim's own signature authorizes the theft. Mitigation exists only client-side (decoding the auth tree and rejecting unexpected children), which the threat model itself assigns to the client rather than the contracts — nothing on-chain prevents it.

### Recommendation
- Bound what a route can invoke on-chain: have the router restrict payload-named `pool`/`token` addresses to a venue allowlist, or have the controller deliver output measurement and reject auth trees that gain children — e.g., by isolating the router call behind an intermediate contract the caller does not authorize, so payload `require_auth` on the caller cannot attach to the signed entry.
- Alternatively, make the router pull input via `transfer_from`-style allowance scoped to its own auth (contract-as-sender), so the end user never signs an auth tree that route-named code can extend.
- Until a contract fix exists, wallets/SDKs must decode the simulated authorization tree and reject any `sub_invocations` beyond the single expected input transfer (for `execute_strategy`) or the documented nested transfers per verb.

### Proof of Concept
The repository already contains an executable demonstration. `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:

- `UnlistedPoolRouter.execute_strategy` (`:39-47`) decodes caller-supplied `swap_xdr`, then `env.invoke_contract(&route.hop_pool, "swap", …)` — arbitrary contract, chosen by whoever built the bytes.
- `RogueHopPool.swap` (`:62-71`) calls `token.transfer(alice → attacker, WALLET_BALANCE)` on a wallet token, relying on Alice's `require_auth` being satisfiable inside her signed tree.
- Alice submits `controller.swap_collateral(alice, account_id, USDC, 5_000 USDC, ETH, route)` (`:147-157`). Simulation records the theft as a child of her `swap_collateral` auth (`:206-222`); the assertion shows `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`, and the swap still credits her `FAIR_OUT_ETH` — every protocol check passes.

Signing the recorded tree in enforcing mode makes the theft real. To reproduce: supply USDC as Alice, register the rogue pool with a `(alice, wallet_token, attacker, amount)` plan, build route bytes naming it, simulate `swap_collateral`, sign the returned auth tree, submit.