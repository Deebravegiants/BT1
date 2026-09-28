### Title
Tokens sent directly to the pool are permanently uncredited and absorbed as unbooked liquidity - (File: contracts/pool + controller measured-receipt settlement)

### Summary
The Footium bug class is "a payment succeeds even though the referenced entity does not exist, so the funds are accepted by the contract but never associated with anything." The controller correctly rejects the on-book version of this (`repay`/`supply` to a non-existent `account_id` revert), but the same class survives on the pool's physical-custody edge: any address can `transfer` tokens straight to the pool contract. The transaction succeeds, no market's cash book records the receipt, no shares are minted, and no entrypoint can return the funds.

### Finding Description
All legitimate inflows go through measured-receipt settlement: `process_deposit` credits only what `payments::transfer_amount_measured` observes and pushes a `PoolSupplyEntry` into `pool_supply_call`, and `repay`/`recapitalize` do the same with excess refunded to the payer (`contracts/controller/src/positions/supply.rs` `process_deposit`, `contracts/controller/src/external/pool.rs` `pool_repay_call`). The pool's accounting is book-based: `cash`, `supplied`, `borrowed`, `revenue` are tracked per `(hub_id, asset)` over one shared physical token balance.

A direct `token.transfer(payer, pool, amount)` bypasses that entirely. The money-flow audit test proves the result: after an unsolicited transfer, `token.balance(pool) == state.cash + other.cash + 7 * UNIT`, i.e., the donation "belongs to no market's cash book" (`tests/test-harness/tests/pool_money_flow_audit.rs:86-95`). Because borrows, withdrawals, and liquidation payouts draw on the physical balance while every book ignores the stray amount, the tokens silently become withdrawable liquidity backing other users' positions, and no permissionless or privileged path reconciles the surplus — `recapitalize` applies only the measured receipt up to a recorded shortfall and refunds the excess, and `claim_revenue` sweeps only accrued book revenue.

Every analogous guard against the bug does exist one layer up — `storage::get_account` panics `AccountNotFound` on a missing account and `test_repay_rejects_nonexistent_account_id` asserts the revert — but nothing guards the raw token edge, exactly like Footium's missing existence check on `_clubId`.

### Impact Explanation
Permanent freezing / effective theft of the sender's funds: the transferred tokens are locked inside the pool with no claimable share, and because withdrawals and borrows pay out of the physical balance, the stray amount is consumed to service other users — the donor loses the funds while the protocol never credits them to any account or market, matching the Footium impact (payment accepted, attributed to nothing, transaction does not revert).

### Likelihood Explanation
Medium, same as the source finding. It requires a user error — sending tokens directly to the pool address instead of calling `controller::supply` — which is plausible because the pool address is a well-known protocol contract and integrators/wallets routinely expose raw transfer paths. No attacker action is needed; any unprivileged holder of the token can trigger it accidentally.

### Recommendation
Accept that plain SAC transfers cannot be blocked, but close the accounting gap:

- Add a permissionless sweep (e.g., inside `claim_revenue` or a dedicated entrypoint) that reconciles `token.balance(pool)` against the sum of all markets' booked cash and routes the surplus to the revenue accumulator, so stray funds at least become protocol revenue rather than silently backing other users' withdrawals.
- Alternatively, let `recapitalize` recognize pre-existing physical surplus above the booked cash as an eligible donation source instead of only crediting the measured in-call receipt.
- Document the hazard in the controller README so integrators never construct a raw `token.transfer` to the pool.

### Proof of Concept
```rust
// tests/test-harness/tests/pool_money_flow_audit.rs:86-95 (existing behavior)
// An unsolicited donation belongs to no market's cash book.
market.token_admin.mint(&payer, &(7 * UNIT));
token.transfer(&payer, &market.pool, &(7 * UNIT));   // succeeds, no revert
// token.balance(&market.pool) == state.cash + other.cash + 7 * UNIT
// => the 7 * UNIT is credited to no account, no market book, no revenue;
//    it is unrecoverable yet physically spendable by borrows/withdrawals.
```
Contrast with the on-book path, which correctly reverts: `ctrl.repay(&caller, &999_999u64, &payments)` fails with `ACCOUNT_NOT_IN_MARKET` (`test_repay_rejects_nonexistent_account_id`), and `supply`/`withdraw` hit `storage::get_account` → `AccountNotFound` before any transfer. Only the direct-to-pool edge accepts funds for an entity that will never exist in the books.