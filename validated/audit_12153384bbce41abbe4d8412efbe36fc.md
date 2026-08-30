### Title
Oracle timestamp-freshness check treats any future publish time as automatically "fresh," permanently poisoning the monotonic price cache - ([File: mainnet/contracts/market/v0-4-market.clar])

### Summary
`oracle-timestamp-fresh()` in `mainnet/contracts/market/v0-4-market.clar` is intended to reject stale oracle prices, but its handling of a future timestamp is inverted: instead of rejecting a `_timestamp` that is ahead of `block.timestamp` (the bug class flagged in the external report), the function forces the staleness `delta` to `u0` whenever `ts > stacks-block-time`, which makes the freshness check trivially pass for *any* future timestamp, no matter how far ahead it is.

### Finding Description
```clarity
(define-private (oracle-timestamp-fresh (ts uint) (prev uint) (max-staleness uint))
  (let ((delta (if (> ts stacks-block-time)
                   u0
                   (- stacks-block-time ts))))
    (and
      (<= delta max-staleness)
      (>= ts prev))))
``` [1](#0-0) 

This is called from `price-resolve`, which uses it to gate whether a freshly-fetched oracle price is accepted and whether the monotonic `last-update` timestamp map entry is advanced:
```clarity
(asserts! (and (oracle-price-legal final-price) (oracle-timestamp-fresh timestamp last-update-time max-staleness))
          ERR-ORACLE-INVARIANT)
(if (> timestamp last-update-time)
    (map-set last-update key timestamp)
    false)
``` [2](#0-1) 

The upstream feeds (`resolve-pyth`/`resolve-dia`) simply pass through whatever `publish-time`/`timestamp` the feed contract reports, with `resolve-dia` even doing unit math (`ms → s`) on it. [3](#0-2) 

The intended semantics mirror the report's identity: a valid timestamp should satisfy `block.timestamp - max_staleness <= ts <= block.timestamp`. Instead the code implements: "if `ts` is in the future, treat staleness as `0`" — i.e., `ts > block.timestamp ⇒ always fresh`, which is strictly worse than the reported Blex bug (which at least bounded the future deviation by `_maxTimeDeviation`). Here there is no bound at all on how far into the future `ts` can be.

Because `price-resolve` also updates the monotonic `last-update` map only when the new `timestamp` exceeds the stored one, accepting one erroneous future timestamp poisons that map entry: every subsequent legitimate (correctly-timed) price update will have `ts` (real, current) `< prev` (the erroneous future value), so `(>= ts prev)` fails and `oracle-timestamp-fresh` returns `false` for the asset until `stacks-block-time` finally catches up to the erroneous future value. During that entire window, `price-resolve` reverts with `ERR-ORACLE-INVARIANT` for that asset/feed key, so every operation that requires pricing that asset (borrow, withdraw, repay, health checks, liquidation) is blocked.

### Impact Explanation
This breaks the intended value/availability identity that "the oracle price used equals the true current market price within `max-staleness`." A single anomalous future timestamp (e.g., from a Pyth/DIA relay clock-skew bug — the very failure mode acknowledged in the reference report) causes:
1. An arbitrarily stale/incorrect price to be accepted as "fresh" with no upper time bound, letting the market compute collateral/debt values, health factors, and liquidation eligibility off a bogus price — enabling incorrect liquidations, missed liquidations, or under-collateralized borrows (protocol insolvency risk).
2. Once accepted, the `last-update` map is permanently advanced past the current time, causing **freezing of that asset's pricing/liquidation functionality** for the entire duration until real time catches up to the injected future timestamp (which could be arbitrarily long depending on how far in the future the bad timestamp was).

This satisfies both "protocol insolvency" (Critical) and "temporary freezing of funds" (High) categories depending on how the bad price is exploited before/while the freeze occurs.

### Likelihood Explanation
This does not require any privileged compromise of Zest's own contracts — it is triggered purely by the price-feed value (`publish-time`) that the market contract consumes, exactly analogous to the referenced report where an off-chain price-updater bug produced a future timestamp. The market contract's own defensive check (`oracle-timestamp-fresh`) fails to prevent it and, worse, actively short-circuits the staleness computation for exactly this case, making the check strictly weaker than intended rather than merely imperfect.

### Recommendation
Rewrite `oracle-timestamp-fresh` to reject any timestamp greater than the current block time outright, rather than special-casing it to `delta = 0`:
```clarity
(define-private (oracle-timestamp-fresh (ts uint) (prev uint) (max-staleness uint))
  (and
    (<= ts stacks-block-time)
    (<= (- stacks-block-time ts) max-staleness)
    (>= ts prev)))
```
This ensures `ts <= block.timestamp` is enforced (matching the report's recommended fix of `_timestamp <= block.timestamp`), preventing both the improper acceptance of future prices and the resulting permanent poisoning of the `last-update` monotonic map.

### Proof of Concept
1. Pyth (or DIA) relayer, due to a clock-skew/off-chain bug (as acknowledged in the analogous report), submits a price update with `publish-time` = `block.timestamp + 10_000_000` (far future) for an asset feed.
2. `resolve-pyth`/`resolve-dia` returns this `timestamp` unchanged to `price-resolve`. [3](#0-2) 
3. `price-resolve` calls `oracle-timestamp-fresh(timestamp, last-update-time, max-staleness)`; since `timestamp > stacks-block-time`, `delta` is forced to `u0`, so `(<= delta max-staleness)` is `true`, and `(>= ts prev)` is `true` since the future timestamp exceeds any prior value — the check passes and the bogus price is used. [1](#0-0) 
4. `map-set last-update key timestamp` stores the future timestamp as the new baseline. [4](#0-3) 
5. All subsequent, correctly-timed price updates for that feed key have `ts` (current, real) `< prev` (the erroneous future value), so `(>= ts prev)` now fails, and `price-resolve` reverts with `ERR-ORACLE-INVARIANT` for every call needing that asset's price — freezing borrow/repay/withdraw/liquidation for that asset until real time passes the erroneous future timestamp.

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L312-330)
```text
(define-private (resolve-pyth (ident (buff 32)))
  (let ((response (try! (call-pyth ident)))
        (price (get price response))
        (expo (get expo response))
        (conf (get conf response))
        (final-price (normalize-pyth price expo))
        (timestamp (get publish-time response)))
    (try! (check-confidence price conf))
    (ok { value: final-price, timestamp: timestamp })))

(define-private (call-dia (key (string-ascii 32)))
  (let ((res (unwrap! (contract-call? 'SP1G48FZ4Y7JY8G2Z0N51QTCYGBQ6F4J43J77BQC0.dia-oracle get-value key) ERR-ORACLE-DIA)))
    (ok res)))

(define-private (resolve-dia (ident (buff 32)))
  (let ((key (unwrap-panic (from-consensus-buff? (string-ascii 32) ident)))
        (res (try! (call-dia key))))
    ;; DIA returns timestamp in milliseconds, convert to seconds for staleness check
    (ok { value: (get value res), timestamp: (/ (get timestamp res) u1000) })))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L365-371)
```text
(define-private (oracle-timestamp-fresh (ts uint) (prev uint) (max-staleness uint))
  (let ((delta (if (> ts stacks-block-time)
                   u0
                   (- stacks-block-time ts))))
    (and
      (<= delta max-staleness)
      (>= ts prev))))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L386-393)
```text
    ;; validate price and timestamp using max-staleness from oracle data
    (asserts! (and (oracle-price-legal final-price) (oracle-timestamp-fresh timestamp last-update-time max-staleness))
              ERR-ORACLE-INVARIANT)

    ;; update timestamp if newer
    (if (> timestamp last-update-time)
        (map-set last-update key timestamp)
        false)
```
