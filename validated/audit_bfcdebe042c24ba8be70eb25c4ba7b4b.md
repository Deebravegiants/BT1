### No vulnerability found for this question.

**Analysis supporting this conclusion:**

`normalize-pyth` at [1](#0-0)  computes `adj = expo + 8` and short-circuits via `asserts!` when `adj = 0`, returning `(to-uint p)`. In the general branch, when `adj = 0` the code takes the `else` path `(/ p (pow 10 (- adj)))` = `(/ p (pow 10 0))` = `(/ p 1)` = `p`, then applies the same `(to-uint res)`. Both paths therefore produce an identical result — the `asserts!` is a pure optimization to skip a redundant division by 1, not a divergent code path. There is no case where the early-return value differs from what the "full" computation would have produced.

Additionally, `to-uint` on a negative `int` in Clarity aborts the transaction at runtime rather than silently wrapping, so a negative Pyth price cannot slip through as an inflated unsigned value.

Finally, `collateral-remove` at [2](#0-1)  uses `price-resolve` (which calls `normalize-pyth` indirectly) only to compute collateral/debt USD values for health checks (`is-healthy`, `ERR-INSUFFICIENT-COLLATERAL`). It never writes to the `debt` map or records a "repayment" — actual debt/repayment bookkeeping happens in separate repay functions, not in `collateral-remove`. The vault call at line 1156 (`v0-market-vault collateral-remove`) only moves collateral amounts, not debt.

Since `normalize-pyth`'s two branches are mathematically equivalent and `collateral-remove` never mutates the `debt` map or `total-debt`, the claimed invariant break (sum of `debt * index` vs `total-debt`) is not reachable through this path.

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L297-303)
```text
(define-private (normalize-pyth (p int) (expo int))
  (let ((adj (+ expo 8))
        (inkind? (asserts! (not (is-eq adj 0)) (to-uint p)))
        (res (if (> adj 0)
                (* p (pow 10 adj))
                (/ p (pow 10 (- adj))))))
    (to-uint res)))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1136-1161)
```text
          (asserts! (is-healthy collateral-value debt-value current-ltvb) ERR-UNHEALTHY)
          (asserts!
            (if is-collateral-enabled
                (let ((t (asserts! (>= collateral-value removed-asset-value) ERR-INSUFFICIENT-COLLATERAL))
                      (post-removal-collateral-value (- collateral-value removed-asset-value)))
                  (if removing-all
                      (let ((future-mask (bit-and position-mask (bit-not (pow u2 asset-id)))))
                        (try! (is-healthy-with-mask post-removal-collateral-value debt-value future-mask)))
                      (is-healthy post-removal-collateral-value debt-value current-ltvb)))
                (let ((oracle-data (get oracle asset))
                      (price (unwrap! (price-resolve oracle-data) ERR-DISABLED-COLLATERAL-PRICE-FAILED))
                      (decimals (get decimals asset))
                      (user-amount (find-collateral-amount (get collateral pos-full) asset-id))
                      (disabled-notional (normalize (* user-amount price) decimals false))
                      (removal-notional (normalize (* amount price) decimals true))
                      (total-collateral-value (+ collateral-value disabled-notional)))
                  (asserts! (>= total-collateral-value removal-notional) ERR-INSUFFICIENT-COLLATERAL)
                  (is-healthy (- total-collateral-value removal-notional) debt-value current-ltvb)))
            ERR-UNHEALTHY)

          (let ((result (try! (contract-call? .v0-market-vault collateral-remove account amount ft asset-id collateral-receiver))))
            (print { action: "collateral-remove", caller: contract-caller,
                     data: { account: account, receiver: collateral-receiver, asset-id: asset-id,
                             asset-addr: ft-address, amount: amount, updated-collateral-amount: result,
                             position-collateral-usd: collateral-value, position-debt-usd: debt-value }})
            (ok result)))
```
