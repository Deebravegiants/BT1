### Title
Pool `flash` commits a stale market snapshot after the receiver callback, clobbering concurrent market mutations - (File: contracts/pool/src/ops/flash.rs)

### Summary
The reported bug class is "a function that assumes a lock is held is invoked without it, so a concurrently freed/mutated object is used" — i.e., state observed before an unguarded window is used after it. The pool's flash loan `apply()` loads the entire market into a `Cache` in `prepare()`, invokes an arbitrary receiver contract, then blindly commits that pre-callback snapshot in `finalize()`. There is no reentrancy guard in the pool: the `FlashLoanOngoing` flag lives in *controller* storage and is only set by the controller's own strategy wrappers (`with_flash_guard`), never by `pool::flash`. During the receiver callback, the receiver can reach controller entrypoints (which are not guarded, since the controller flag is unset) that write to the same pool market; `finalize()` then writes back the stale cache, silently losing the concurrent mutation.

### Finding Description
`apply()` in `contracts/pool/src/ops/flash.rs:40-71`:

1. `prepare()` → `ops::renewed_market` loads and accrues the market into `cache` (line 48, 79).
2. Principal is paid out and the receiver's `execute_flash_loan` is invoked (line 62-64) — an arbitrary WASM contract controlled by the caller.
3. `finalize()` → `book_fee` + `cache.commit()` writes the market state captured at step 1 back to storage (line 69, 133-136).

No flag is set on the pool side around step 2. The only reentrancy flag, `SessionKey::FlashLoanOngoing` in `contracts/controller/src/storage/account.rs:278-313`, is set exclusively by `with_flash_guard`, which wraps only the controller's `flash_loan` and `flash_position` strategy internals — it is never set when the pool's own `flash_loan` path runs. Consequently, inside `execute_flash_loan` the receiver can call e.g. `controller.supply(...)`, `repay`, `liquidate`, `update_indexes`, or `claim_revenue` on the same `hub_asset`, each of which performs a cross-contract write to the pool's market entry (cash, indexes, scaled supply/debt, revenue). When the callback returns, `require_balance` only checks the *token balance* equals `balance_after_payout` (line 66) — storage state is never revalidated. `cache.commit()` then overwrites the market with the stale snapshot, discarding the nested mutation: index accruals, cash deltas, or revenue shares booked by the nested call are lost.

This is structurally identical to the CVE: `hci_connect_cfm` assumed `hdev->lock` (mutual exclusion over the conn object); here `finalize`/`commit` assumes exclusive ownership of the market entry across the callback, and nothing enforces it.

### Impact Explanation
A nested `update_indexes`/`supply`/`repay` on the same market is committed by the pool's ops layer, then overwritten by the flash cache. Effects depending on what is clobbered:

- Index accrual loss: interest accrued in the nested call is reverted, while the debt position scaled at the higher index remains — borrowers are under-charged → protocol insolvency / revenue theft.
- If the nested call reduced `cash`/`scaled_supply` bookkeeping relative to the stale cache (e.g., a seize or withdraw recorded in raw fields), the stale commit restores balances without the corresponding tokens, breaking the balance-vs-bookkeeping invariant the flash flow itself relies on (INV-FLASH-01), enabling later withdrawals of unbacked funds.

### Likelihood Explanation
Reachable by a single unprivileged address: deploy a receiver contract implementing `execute_flash_loan`, call the pool flash entrypoint (or the controller `flash_loan` strategy path — but the pool path is the unguarded one), and inside the callback invoke any non-guarded controller entrypoint touching the same `hub_asset`. No timing luck is needed; the callback is synchronous by construction. Requires the market to be `is_flashloanable` and have `amount` in reserves.

### Recommendation
Hold the "lock": set a reentrancy flag in the pool (or have the pool set `FlashLoanOngoing` in controller storage) around `invoke_receiver` in `contracts/pool/src/ops/flash.rs`, and reject reentry into controller entrypoints that mutate pool market state while it is set — mirroring how `with_flash_guard` already guards the controller's own flash strategies. Alternatively, reload/merge the market from storage before `cache.commit()` instead of writing back the pre-callback snapshot.

### Proof of Concept
1. Attacker deploys receiver contract `R` implementing `execute_flash_loan`.
2. Attacker calls the pool flash loan for `hub_asset = A`, `amount` near reserves.
3. Inside `execute_flash_loan`, `R` calls `controller.update_indexes(A)` (or `repay`/`claim_revenue` on market `A` with a prepared account), which accrues interest and writes market state `M'`.
4. Callback returns; `require_balance` passes (token balance unchanged by the storage-only call).
5. `finalize` → `cache.commit()` writes the pre-callback market `M`, discarding `M'`'s accrued index while position state written by the nested call persists — the books now disagree with scaled positions.

*Caveat on completeness:* I verified the unguarded callback window and the controller-only scope of `FlashLoanOngoing`; I did not fully trace `cache.commit()`'s write granularity (whole-struct vs. field merge) or the exact pool authorization checks on nested controller calls. If `commit()` merges fields or nested writes are impossible, the clobber would not occur — but the balance-only postcondition and the stale-snapshot writeback pattern strongly suggest it does.