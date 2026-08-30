### Title
Liquidation transactions revert entirely when any position asset's oracle price is stale/invalid, blocking liquidation of insolvent positions - (File: `mainnet/contracts/market/v0-4-market.clar`)

### Summary
The `liquidate()` function unconditionally requires *fresh, positive* oracle prices for every enabled asset in a borrower's position mask before it can compute health/LTV and execute a liquidation. If even one asset price fails the `oracle-price-legal`/`oracle-timestamp-fresh` check, the whole liquidation transaction reverts via a hard `unwrap-panic`, exactly mirroring the Tapioca H-37 root cause where `Market.updateExchangeRate()` reverts instead of falling back to an old rate during liquidation.

### Finding Description
`liquidate()` calls `get-assets(mask)` to build the priced asset list used for LTV/notional evaluation: [1](#0-0) 

`get-assets` resolves prices for *all* enabled assets in the position's bitmap via `price-multi-resolve`, and hard-panics if resolution fails for any of them: [2](#0-1) 

`price-multi-resolve` asserts that every entry in the fold succeeded, aborting with `ERR-ORACLE-MULTI` otherwise: [3](#0-2) 

Each individual `price-resolve` call asserts both `oracle-price-legal` (price `> 0`) and `oracle-timestamp-fresh` (staleness bound), reverting with `ERR-ORACLE-INVARIANT` if either check fails: [4](#0-3) 

Because `liquidate()` uses `try!`/`unwrap-panic` on this entire chain with no fallback path, any single asset (even one only tangentially enabled on the position, not the specific collateral/debt pair being liquidated) having a momentarily stale or zero price aborts the *entire* liquidation call: [5](#0-4) 

This is the same root-cause pattern as the referenced Tapioca H-37: a liquidation-critical price fetch path has a hard revert-on-invalid-data behavior instead of the "liquidations should never fail" fallback design that the rest of the protocol relies on for solvency guarantees.

### Impact Explanation
While liquidations are blocked, a borrower's collateral value can continue to fall below their debt value without any way for liquidators to intervene, since `liquidate()` cannot even begin its health/LTV computation. This can push the protocol toward **insolvency** (bad debt accumulating beyond what would have been captured by timely liquidation), which is an in-scope Critical impact bucket (protocol insolvency).

### Likelihood Explanation
Oracle staleness (feed not updated within `max-staleness`) or a momentary invalid (`<= 0`) price on any enabled asset is a realistic operational condition, not one requiring an attacker to compromise the DAO or perform any privileged action — it can occur passively from oracle publisher downtime combined with the caller not supplying (or being unable to supply, e.g. for DIA-sourced assets with no `price-feeds` update mechanism in `liquidate`) a fresh update. The `price-feeds` parameter in `liquidate()` only allows pushing Pyth updates via `write-feed`/`verify-and-update-price-feeds`; assets priced via DIA or callcode-derived (zToken/stSTX) prices have no equivalent liquidator-supplied override, so a stale non-Pyth feed cannot be worked around by the liquidator at all: [6](#0-5) 

### Recommendation
For the liquidation code path specifically, do not hard-revert the entire transaction when a price is stale/invalid. Instead, fall back to the last known valid price (or a protocol-configured circuit-breaker price) for assets that are not directly the collateral/debt pair being liquidated, or restrict the price-freshness requirement in `get-assets`/`get-notional-evaluation` during `liquidate()` to only the two assets actually involved in the liquidation call, so an unrelated stale feed cannot block liquidation of an otherwise-liquidatable position.

### Proof of Concept
1. Borrower opens a position enabling collateral assets A and B, and borrows debt asset D.
2. Debt asset D's price rises (or collateral A's price falls) such that the position becomes liquidatable (`current-ltv >= ltv-liq-partial`).
3. Separately, collateral asset B's oracle feed (e.g., a DIA-sourced feed with no liquidator-supplied update path, or a Pyth feed whose `max-staleness` window elapses) goes stale, i.e., `oracle-timestamp-fresh` returns `false` for B (`local-testing/contracts/market/market.clar:387-393`).
4. A liquidator calls `liquidate(borrower, collateral-ft=A, debt-ft=D, ...)`. Internally, `get-assets(mask)` still resolves prices for *all* enabled assets on the position, including B `(local-testing/contracts/market/market.clar:504-514)`.
5. `price-multi-resolve` → `price-resolve` for asset B fails the freshness assertion and returns an `err`, causing `iter-price-multi` to set `valid: false`, which then causes `price-multi-resolve`'s `asserts!` to fire `ERR-ORACLE-MULTI` `(local-testing/contracts/market/market.clar:419-425)`.
6. This error propagates through `unwrap-panic` in `get-assets`, aborting the entire `liquidate()` transaction — even though the liquidation of the A/D pair itself required no information about B's price.
7. The borrower's undercollateralized position remains un-liquidated for as long as B's feed stays stale, allowing further price deterioration and accumulation of bad debt.

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L1382-1413)
```text
(define-public (liquidate
                (borrower principal)
                (collateral-ft <ft-trait>)
                (debt-ft <ft-trait>)
                (debt-amount uint)
                (min-collateral-expected uint)
                (collateral-receiver (optional principal))
                (price-feeds (optional (list 3 (buff 8192)))))
  (let (
    (feeds-check (try! (write-feeds price-feeds)))
    (liquidator contract-caller)
    (position (try! (get-liquidation-position borrower)))
    (pos-full (try! (get-full-position borrower)))
    (mask (get mask position))
    (group (try! (get-egroup mask)))

    (coll-address (contract-of collateral-ft))
    (debt-address (contract-of debt-ft))
    (coll-asset (try! (get-asset coll-address)))
    (debt-asset (try! (get-asset debt-address)))
    (coll-aid (get id coll-asset))
    (debt-aid (get id debt-asset))

    ;; accrue FIRST - populates cache for zToken price resolution
    (u-debt (accrue-user-debts (get debt pos-full)))
    (u-coll (accrue-user-collateral (get collateral pos-full)))

    ;; NOW safe to resolve prices (cache is populated)
    (assets (get-assets mask))
    (notional-valued-assets (get-notional-evaluation { position: position, assets: assets }))
    (total-collateral-usd (get collateral notional-valued-assets))
    (total-debt-usd (get debt notional-valued-assets))
```

**File:** local-testing/contracts/market/market.clar (L133-160)
```text
(define-private (write-feed (feed (buff 8192)) (status (response bool uint)))
  (match status
    success-status
      ;; @mainnet: (match (contract-call? 'SP1CGXWEAMG6P6FT04W66NVGJ7PQWMDAC19R7PJ0Y.pyth-oracle-v4 verify-and-update-price-feeds
      (match (contract-call? .pyth-oracle-v4 verify-and-update-price-feeds
          feed
          {
            ;; @mainnet: pyth-storage-contract: 'SP1CGXWEAMG6P6FT04W66NVGJ7PQWMDAC19R7PJ0Y.pyth-storage-v4,
            pyth-storage-contract: .pyth-storage-v4,
            ;; @mainnet: pyth-decoder-contract: 'SP1CGXWEAMG6P6FT04W66NVGJ7PQWMDAC19R7PJ0Y.pyth-pnau-decoder-v3,
            pyth-decoder-contract: .pyth-pnau-decoder-v3,
            ;; @mainnet: wormhole-core-contract: 'SP1CGXWEAMG6P6FT04W66NVGJ7PQWMDAC19R7PJ0Y.wormhole-core-v4,
            wormhole-core-contract: .wormhole-core-v4,
          }
        )
        update-success (ok true)
        update-failed ERR-PRICE-FEED-UPDATE-FAILED)
    error-status status
  )
)

;; Process optional list of price feed updates
;; If list is provided, folds over it and updates all feeds
;; If list is none, does nothing (allows for backward compatibility)
(define-private (write-feeds (feeds (optional (list 3 (buff 8192)))))
  (match feeds
    entries (fold write-feed entries (ok true))
    (ok true)))
```

**File:** local-testing/contracts/market/market.clar (L384-410)
```text
(define-private (oracle-price-legal (p uint))
  (> p u0))

(define-private (oracle-timestamp-fresh (ts uint) (prev uint) (max-staleness uint))
  (let ((delta (if (> ts stacks-block-time)
                   u0
                   (- stacks-block-time ts))))
    (and
      (<= delta max-staleness)
      (>= ts prev))))

(define-private (price-resolve
  (data { type: (buff 1), ident: (buff 32), callcode: (optional (buff 1)), max-staleness: uint }))
  (let ((type (get type data))
        (ident (get ident data))
        (key { type: type, ident: ident })
        (resolution (try! (resolve-price-feed type ident)))
        (price (get value resolution))
        (callcode (get callcode data))
        (final-price (try! (resolve-callcode price callcode)))
        (last-update-time (oracle-last-update key))
        (timestamp (get timestamp resolution))
        (max-staleness (get max-staleness data)))

    ;; validate price and timestamp using max-staleness from oracle data
    (asserts! (and (oracle-price-legal final-price) (oracle-timestamp-fresh timestamp last-update-time max-staleness))
              ERR-ORACLE-INVARIANT)
```

**File:** local-testing/contracts/market/market.clar (L419-425)
```text
(define-private (price-multi-resolve
  (data (list 64 { type: (buff 1), ident: (buff 32), callcode: (optional (buff 1)), max-staleness: uint }))
  (aids (list 64 uint)))
  (let ((init { output: (list), valid: true, aids: aids, idx: u0 })
        (response (fold iter-price-multi data init)))
    (asserts! (get valid response) ERR-ORACLE-MULTI)
    (ok (get output response))))
```

**File:** local-testing/contracts/market/market.clar (L504-514)
```text
(define-private (get-assets (mask-user uint))
  (let ((mask-enabled (get-enabled-bitmap))
        (safe-mask (user-safe-mask mask-user mask-enabled))
        (iter (mask-to-list-collateral safe-mask))
        (assets-list (get-status-multi iter))
        (oracles-list (map get-oracle assets-list))
        ;; Extract asset-ids for price resolution
        (asset-ids (map get-asset-id assets-list))
        ;; Use internal price resolution
        (prices-list (unwrap-panic (price-multi-resolve oracles-list asset-ids))))
    (map merge-price assets-list prices-list)))
```
