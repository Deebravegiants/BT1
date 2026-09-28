### Title
Suppliers cannot specify a minimum payout on `withdraw`, so a front-running bad-debt socialization writes down the supply index and the full withdrawal pays less than the observed balance - (File: contracts/pool/src/ops/withdraw.rs)

### Summary
The Velar finding is the classic "burn pays a pro-rata share of a mutable pool value with no min-out" bug. XOXNO Lending has the same shape on its exit path: a withdraw request of `0` means "withdraw all" and pays `floor(position_shares × supply_index)` — a quantity that is not fixed at submission time. Any unprivileged address can call `clean_bad_debt` (or `liquidate` on an account that becomes socializable) and write down the supply index via `apply_bad_debt_to_supply_index` before the supplier's withdraw executes. The supplier's transaction then succeeds but pays strictly less than the balance observed off-chain, and there is no `min_amount`/`slippage` parameter on `withdraw` to bound the loss.

### Finding Description
- `process_withdraw` maps a `0` amount leg to `WITHDRAW_ALL_SENTINEL` and forwards `PoolWithdrawEntry` with no minimum-received field (`contracts/controller/src/positions/supply.rs:140-215`). The entry only carries `action` and `protocol_fee`.
- In the pool, `resolve_withdrawal` treats `amount >= half_up(scaled × index)` as a full close and pays `unscale_supply_floor(scaled, supply_index)` (`common/src/rates/scaling.rs:105-121`, `contracts/pool/src/cache/scale.rs:97-105`). The payout is computed at execution time from the committed `supply_index`.
- `supply_index` can decrease between transaction construction and execution: `apply_bad_debt_to_supply_index` reduces it pro-rata to socialized debt (`contracts/pool/src/interest.rs:73-80`), invoked from `execute_bad_debt_cleanup`, reachable permissionlessly through `clean_bad_debt` when the insolvent account's collateral is at or below the $5 dust cap, or automatically inside `liquidate` via `check_bad_debt_after_liquidation` (`contracts/controller/src/positions/liquidation/mod.rs:195-243`, `apply.rs:300-316`).
- Tests confirm the write-down transfers value away from all suppliers of that market: `test_keeper_clean_bad_debt_decreases_supply_index` and `test_bad_debt_reduction_matches_formula` show Bob's supply balance falling by `balance × (1 - index_ratio)` with no compensating credit (`tests/test-harness/tests/controller/bad_debt_index.rs:196-277`).

Unlike partial withdrawals — which are amount-denominated and therefore self-protecting — the full-close path is share-denominated in effect: the user requests "all my shares" and accepts whatever `floor(shares × index)` evaluates to at execution.

### Impact Explanation
A supplier who observes a withdrawable balance B and submits `withdraw(account_id, [(hub_asset, 0)])` can receive strictly less than B if a bad-debt socialization on the same (hub, token) market executes first. The loss equals `shares × (index_before − index_after)`, unbounded below by anything in the entrypoint. This is theft-adjacent loss of user funds identical in mechanism to the Velar report: an intervening transaction shrinks the per-share redemption value after the victim's tx is constructed.

### Likelihood Explanation
Requires an insolvent, dust-collateral account in the same market — a state that arises organically after price crashes — plus ordering: the cleanup or liquidation must land before the withdraw. Both `clean_bad_debt` and `liquidate` are permissionless and are precisely the transactions keepers race to submit during volatility, which is also when users race to withdraw. The loss size is bounded by the socialized debt (capped at total supply value), and for large markets the per-user share of the write-down is typically small — consistent with Medium severity.

### Recommendation
Add a `min_amount_out` (minimum gross payout) parameter to the withdraw path — e.g. extend `HubPayment`/`PoolWithdrawEntry` with a floor amount, and in `resolve_close_or_partial`/`gate_and_debit` revert with a dedicated error if the computed `gross_amount` is below the user-supplied floor. This lets full withdrawers bound execution-time index drift, including bad-debt write-downs and floor-vs-half-up rounding.

### Proof of Concept
1. Bob supplies 1000 ETH to market `(hub, ETH)`; his position is `scaled` shares at supply index `I0`, displayed balance `B0 = floor(scaled × I0)`.
2. Alice's account holds ≤ $5 of collateral and > collateral-worth of ETH debt (price crash makes her insolvent and dust-capped).
3. Bob reads `get_collateral_amount` ≈ `B0` and submits `withdraw(account_id, [(hub_asset, 0)])` — amount 0 selects `WITHDRAW_ALL_SENTINEL`, paying `unscale_supply_floor(scaled, I_exec)` (`contracts/controller/src/positions/supply.rs:190-198`, `common/src/rates/scaling.rs:112-116`).
4. Keeper submits `clean_bad_debt(alice_id)`; `socialize_bad_debt` admits the dust-capped insolvent account and calls `execute_bad_debt_cleanup`, which calls `apply_bad_debt_to_supply_index`, setting `I1 = max(I0 × (V − D)/V, RAY/1000) < I0` (`contracts/pool/src/interest.rs:73-80`; confirmed by `test_keeper_clean_bad_debt_decreases_supply_index`).
5. Bob's withdraw executes after the cleanup and pays `floor(scaled × I1) < B0`. The deficit `scaled × (I0 − I1)` is unrecoverable — `recapitalize` restores cash but never the index (docs/reference/invariants.md INV-LIQ-04). Bob had no parameter to reject the execution.

Note: the same under-payment applies to partial withdrawals only in that a deeper write-down can make the position's floor value fall below the requested `amount`, turning it into a full close at the lower value — but the full-withdraw path is the clean analog since it pins no output amount at all.