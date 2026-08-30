[1](#0-0) [2](#0-1)

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L339-358)
```text
(define-private (resolve-ststx (p uint))
  (let ((ratio (unwrap! (call-ststx-ratio) ERR-ORACLE-CALLCODE)))
    (ok (mul-div-down p ratio STSTX-RATIO-DECIMALS))))

(define-private (resolve-ztoken (p uint) (aid uint))
  (let ((cached (unwrap! (get-cached-indexes aid) ERR-ORACLE-CALLCODE))
        (cached-lindex (get lindex cached))
        (scaled (* p cached-lindex)))
    (ok (div-down scaled INDEX-PRECISION))))

(define-private (resolve-callcode (p uint) (callcode (optional (buff 1))))
  (let ((cc (unwrap! callcode (ok p))))
    (if (is-eq cc CALLCODE-STSTX) (resolve-ststx p)
    (if (is-eq cc CALLCODE-ZSTX) (resolve-ztoken p STX)
    (if (is-eq cc CALLCODE-ZSBTC) (resolve-ztoken p sBTC)
    (if (is-eq cc CALLCODE-ZSTSTX) (resolve-ztoken (try! (resolve-ststx p)) stSTX)
    (if (is-eq cc CALLCODE-ZUSDC) (resolve-ztoken p USDC)
    (if (is-eq cc CALLCODE-ZUSDH) (resolve-ztoken p USDH)
    (if (is-eq cc CALLCODE-ZSTSTXBTC) (resolve-ztoken p stSTXbtc)
    ERR-ORACLE-CALLCODE)))))))))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L373-395)
```text
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

    ;; update timestamp if newer
    (if (> timestamp last-update-time)
        (map-set last-update key timestamp)
        false)

    (ok final-price)))
```
