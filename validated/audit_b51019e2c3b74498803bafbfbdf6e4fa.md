### Title
Unvalidated swap payloads let route-selected code inject user token transfers into the signed authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
Controller strategy entrypoints accept opaque `swap: Bytes` and forward it unchanged to the configured router. Because a route can name arbitrary venue contracts, route-selected code executes below the caller's authenticated `swap_collateral` invocation and can require an unrelated token transfer from that caller. The transfer appears as a child of the caller's authorization tree; if the user signs the simulated tree, unrelated wallet funds are stolen even though the swap itself can return a valid output.

### Finding Description
`swap_collateral` passes the user-supplied `swap` bytes to `process_swap_collateral`, which withdraws collateral and calls `withdraw_and_swap_from_supply` with the same payload (`contracts/controller/src/strategies/swap_collateral.rs:27-76`). That reaches `swap_tokens`, which snapshots token balances and calls `router.execute_strategy(&controller, &amount_in, swap)` (`contracts/controller/src/strategies/swap.rs:24-38`).

The controller constrains only its own invoker authorization: `authorize_transfer_as_current` authorizes one exact controller-to-router transfer with no children (`contracts/controller/src/strategies/swap.rs:33-34`; `common/src/token.rs:36-52`). It does not decode the route or restrict which venue/pool addresses the router may invoke. A venue contract named by the payload therefore runs inside the same top-level `caller.require_auth()` context. If that venue calls `token.transfer(victim, attacker, amount)`, the host records the transfer as a child under the victim's `swap_collateral` authorization. Signing the simulated tree authorizes it.

The same primitive applies to `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, and `multiply`'s third-asset `convert_swap`, because all forward opaque route bytes into the same router boundary.

### Impact Explanation
An unprivileged attacker can steal arbitrary tokens held by the victim's wallet, not merely the strategy input. The malicious route can still pay the expected output token, so the controller's positive-output, overspend, solvency, and health checks all pass. The stolen transfer can name any token contract and any amount that the victim's authorization permits.

The victim's supplied collateral and account remain solvent, while unrelated wallet assets are transferred to the attacker. This is theft of user funds.

### Likelihood Explanation
The attack requires the victim to submit a strategy transaction containing a malicious route and to sign the poisoned authorization tree. An attacker can deploy the malicious venue contract without privileges and provide a route that pays a normal output while embedding the extra token transfer. Wallet or client interfaces that display only the strategy parameters, or that do not clearly identify every nested authorization, make the additional transfer easy to miss.

This does not require compromising governance, the router admin, an oracle, token contracts, or private keys.

### Recommendation
Constrain strategy routes to governance-approved venue contracts and reject routes containing unapproved contract addresses before execution. The router boundary should also expose a canonical decoded route rather than accepting opaque bytes that clients cannot safely validate. Clients must additionally decode the route and reject any authorization tree containing calls beyond the expected strategy input transfer.

### Proof of Concept
1. Victim holds supplied USDC collateral and an unrelated token balance.
2. Attacker deploys a venue contract whose swap method calls:
   ```rust
   token::Client::new(&env, &wallet_token)
       .transfer(&victim, &attacker, &wallet_balance);
   ```
3. Attacker constructs a `swap_collateral` route whose hop invokes that venue while still paying a valid amount of the declared output token.
4. Victim calls `swap_collateral(caller, account_id, usdc_market, amount, eth_market, malicious_route)`.
5. `process_swap_collateral` authenticates the victim, withdraws the supplied USDC, and `swap_tokens` forwards `malicious_route` to the configured router.
6. The router invokes the attacker-selected venue. During simulation, the venue's `wallet_token.transfer(victim, attacker, wallet_balance)` is recorded as a child of the victim's `swap_collateral` authorization.
7. Victim signs the simulated authorization tree.
8. The venue transfers all `wallet_balance` to the attacker; the router returns enough ETH for `NoSwapOutput`, solvency, and health checks to pass.