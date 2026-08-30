## Analysis

The report's bug class — a batch/aggregation mechanism that is supposed to treat each item atomically but instead lets partial effects from a failed item leak into committed state — has a direct analog in the `liquidate-multi` batch liquidation path in this codebase.

### Title
Non-atomic per-position liquidation in `liquidate-multi` lets a mid-liquidation failure commit partial debt/collateral state, letting a liquidator's repayment be accepted without receiving collateral - ([File: mainnet/contracts/market/v0-4-market.clar])

### Summary
`liquidate-multi` executes each batch entry via `(map call-liquidate positions)` and always returns `(ok (list-of-per-entry-responses))` [1](#0-0) . `call-liquidate` invokes the public `liquidate` function as a plain in-contract call (not via `contract-call?`) [2](#0-1) . Inside `liquidate`, the debt repayment (`vault-system-repay`), the borrower's debt-ledger write (`debt-remove-scaled`), and the collateral transfer (`collateral-remove`) are executed as three sequential steps guarded individually by `try!` [3](#0-2) . Because the enclosing `liquidate-multi` transaction always evaluates to `(ok ...)` at the top level, Clarity's whole-transaction rollback (which only fires when the *outermost* invoked public function returns `err`) never triggers for the batch. Any step of an individual entry's `liquidate` call that already committed via a genuine `contract-call?` before a later step in that same entry fails is **not** undone — the failure is merely recorded as an `err` element inside the returned list, exactly like the report's `aggregate3({allowFailure:false})`/uncaught-throw pattern, except inverted: here the "resilience" (batch not reverting) is what silently permits partial per-item state to persist.

### Finding Description
`liquidate`'s state-changing sequence is:
1. `(try! (vault-system-repay debt-aid debt-to-repay debt-ft debt-address))` — pulls repayment tokens from the liquidator and credits the vault [4](#0-3) .
2. `(try! (contract-call? .v0-market-vault debt-remove-scaled borrower scaled-to-remove debt-aid))` — reduces the borrower's scaled debt ledger [5](#0-4) .
3. `(try! (contract-call? .v0-market-vault collateral-remove borrower coll-final collateral-ft coll-aid actual-receiver))` — seizes and transfers collateral to the liquidator [6](#0-5) .

In a single, directly-invoked `liquidate` call this is safe: if step 3 fails, the *whole transaction* (whose only public entry point is `liquidate`) returns `err`, so Clarity reverts all state written in steps 1–2 as well.

But when `liquidate` is invoked from `liquidate-multi` (via `map call-liquidate`), it is no longer the top-level function of the transaction — `liquidate-multi` is, and `liquidate-multi` always returns `(ok ...)` regardless of what `liquidate` returned for any entry [7](#0-6) . Because the top-level call succeeds, Stacks commits the entire changeset produced during the transaction. If entry *i* processes a borrower whose collateral for the requested asset was already fully consumed by an earlier entry in the *same batch* (a scenario the code's own comments acknowledge is expected — "Each position can have different: borrower, collateral asset, debt asset" and "Prevents front-running attacks that prevent bad debt socialization" [8](#0-7) ), then for entry *i*:
- Step 1 (`vault-system-repay`) succeeds — the liquidator's tokens are pulled and vault accounting is updated.
- Step 2 (`debt-remove-scaled`) succeeds — the borrower's scaled-debt ledger entry is reduced.
- Step 3 (`collateral-remove`) fails (e.g., insufficient remaining collateral for that asset/id because a prior batch entry already zeroed it out) and `try!` short-circuits `liquidate` with `(err ...)`.

`call-liquidate` returns this `(err ...)` value unmodified into the `map` result list; `liquidate-multi` wraps it in `(ok (list ... err ...))` and the transaction as a whole succeeds. Steps 1 and 2 — already-executed `contract-call?`s — are **not** rolled back, because the only rollback trigger (top-level `err`) never fires.

### Impact Explanation
The liquidator's repayment (vault-side asset inflow / debt-repayment accounting) is permanently accepted and the borrower's individual debt ledger is permanently decremented, while the liquidator receives **no collateral** in exchange, since step 3 never executes. This breaks the value identity that should hold across a liquidation:
```
debt repaid (vault accounting) + debt reduced (market-vault ledger)  ==  collateral seized and transferred to liquidator
```
After the faulty batch entry, the left side has moved (tokens taken, debt reduced) while the right side has not (no collateral moved). This is a direct loss of principal for the liquidator (their repayment is effectively donated with nothing in return) and simultaneously produces a mismatch between the vault's aggregate debt-repaid/reserve accounting and the true collateral custody state for that borrower — the same "custody versus the collateral map" / "per-user debt ledger versus the vault aggregate" identity class explicitly listed as in-scope.

### Likelihood Explanation
`liquidate-multi` is specifically designed and documented to allow multiple entries targeting the *same borrower* across different collateral/debt asset pairs within one batch call, in order to avoid front-running of bad-debt socialization [8](#0-7) . This means the specific ordering scenario (an earlier entry fully consuming a borrower's collateral for one asset such that a later entry's `collateral-remove` fails after `vault-system-repay`/`debt-remove-scaled` already committed) is not a contrived edge case — it is an intended, expected use pattern of the batch API, making the trigger condition realistic for any liquidator batching partial liquidations of an undercollateralized position with mixed collateral types.

### Recommendation
Wrap each entry's full `liquidate` execution in an explicit atomic sub-call boundary (e.g., invoke it through `contract-call?` to itself, or restructure so that all three steps of a single entry either fully commit or are explicitly and manually reverted before returning `err` from `call-liquidate`), rather than relying on `try!` short-circuiting `liquidate` while the outer `map`/`liquidate-multi` swallows the error and still returns `(ok ...)`. Alternatively, perform all three steps for an entry as a single validated operation with pre-checks (recompute available collateral within the batch state) before any of the three cross-contract calls execute, so a doomed entry never partially executes.

### Proof of Concept
1. Borrower has collateral in assets A and B backing debt in asset D, positioned such that liquidating with collateral A alone via `_no-collateral-left` logic fully consumes the position (triggers `bad-debt-socialized` path removing remaining debt) [9](#0-8) .
2. Liquidator calls `liquidate-multi` with two entries for the same `borrower`: entry #1 `{collateral-ft: A, debt-ft: D, ...}`, entry #2 `{collateral-ft: B, debt-ft: D, ...}`.
3. `map call-liquidate` processes entry #1 first: `vault-system-repay`, `debt-remove-scaled`, `collateral-remove` for A all succeed, and bad-debt socialization strips the borrower's remaining debt list of asset D (since no collateral is left per the `no-collateral-left` check).
4. `map` processes entry #2: `vault-system-repay` for D succeeds (liquidator pays), `debt-remove-scaled` may succeed or trivially no-op depending on remaining scaled debt, but `collateral-remove` for asset B fails because the borrower's collateral B has already been reassigned/zeroed by the socialization logic in entry #1's execution context — `try!` short-circuits `liquidate` for entry #2 with `err`.
5. `liquidate-multi` still returns `(ok (list (ok ...) (err ...)))`. The transaction succeeds; entry #2's `vault-system-repay` (and possibly `debt-remove-scaled`) state changes are committed even though the liquidator received no collateral for entry #2's payment.

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L1495-1512)
```text
    ;; execute liquidation
    (try! (vault-system-repay debt-aid debt-to-repay debt-ft debt-address))

    ;; update obligations and socialize bad debt
    (let ((debt-updated (try! (contract-call? .v0-market-vault
                              debt-remove-scaled
                              borrower
                              scaled-to-remove
                              debt-aid)))
          ;; Collateral receiver defaults to liquidator if not specified
          (actual-receiver (match collateral-receiver recv recv liquidator))
          (coll-removed (try! (contract-call? .v0-market-vault
                              collateral-remove
                              borrower
                              coll-final
                              collateral-ft
                              coll-aid
                              actual-receiver)))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1526-1560)
```text
          (no-collateral-left (and
                                (is-eq coll-removed u0)
                                (or
                                  (is-eq (len (get collateral pos-full)) u1)
                                  (and
                                    (is-eq (len (get collateral pos-full)) (len (get collateral position)))
                                    (is-eq other-debt-repayable u0))))))

      ;; Handle bad debt socialization if no collateral left
      (let ((bad-debt-socialized 
              (if no-collateral-left
                  (let ((stripped-debt-list (filter-out-debt-asset (get debt pos-full) debt-aid))
                        (fresh-debt-list (if (is-eq debt-updated u0)
                                             stripped-debt-list
                                             (unwrap-panic (as-max-len?
                                               (append stripped-debt-list
                                                       { aid: debt-aid, scaled: debt-updated })
                                               u64)))))
                    (if (> (len fresh-debt-list) u0) ;; if still has debt
                      (let ((socialization-result (fold socialize-debt-asset 
                                                        fresh-debt-list 
                                                        { borrower: borrower, success: true })))
                        (asserts! (get success socialization-result) ERR-BAD-DEBT-SOCIALIZATION-FAILED)
                        ;; emit bad-debt-socialized event
                        (print {
                          action: "bad-debt-socialized",
                          caller: contract-caller,
                          data: {
                            borrower: borrower,
                            debt-list: fresh-debt-list
                          }
                        })
                        true)
                      false))
                  false)))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1587-1592)
```text
;; Liquidates multiple positions atomically
;; Each position can have different: borrower, collateral asset, debt asset, and debt amount
;; Prevents front-running attacks that prevent bad debt socialization
;; Note: price-feeds not supported in batch - update prices separately or use individual liquidate()
;; Returns list of responses - one per position (ok/err)
;; Failed liquidations return error codes but don't revert entire batch
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1593-1599)
```text
(define-public (liquidate-multi
                (positions (list 64 { borrower: principal,
                                      collateral-ft: <ft-trait>,
                                      debt-ft: <ft-trait>,
                                      debt-amount: uint,
                                      min-collateral-expected: uint })))
  (ok (map call-liquidate positions)))
```

**File:** local-testing/contracts/market/market.clar (L929-940)
```text
(define-private (call-liquidate (position { borrower: principal,
                                            collateral-ft: <ft-trait>,
                                            debt-ft: <ft-trait>,
                                            debt-amount: uint,
                                            min-collateral-expected: uint }))
  (liquidate (get borrower position)
             (get collateral-ft position)
             (get debt-ft position)
             (get debt-amount position)
             (get min-collateral-expected position)
             none   ;; collateral-receiver defaults to liquidator
             none)) ;; price-feeds not supported in batch - update prices separately
```
