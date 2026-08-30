[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L273-293)
```text
(define-private (accrue-collateral-asset
  (coll-entry { aid: uint, amount: uint })
  (acc { success: bool }))
  (let ((aid (get aid coll-entry)))
    ;; Only accrue if asset is a registered ztoken
    (if (is-ztoken aid)
        ;; ZToken: map to underlying vault routing ID and accrue
        ;; zSTX(1)->STX(0), zsBTC(3)->sBTC(2), zstSTX(5)->stSTX(4), zUSDC(7)->USDC(6), zUSDH(9)->USDH(8), zstSTXbtc(11)->stSTXbtc(10)
        (let ((vault-id (if (is-eq aid zSTX) STX
                        (if (is-eq aid zsBTC) sBTC
                        (if (is-eq aid zstSTX) stSTX
                        (if (is-eq aid zUSDC) USDC
                        (if (is-eq aid zUSDH) USDH
                        (if (is-eq aid zstSTXbtc) stSTXbtc
                        ;; will cause ERR-UNKNOWN-VAULT with any value over 64
                        u100))))))))
          (begin
            (unwrap-panic (accrue-and-cache vault-id))
            acc))
        ;; Non-ztoken: skip accrual (no liquidity index needed)
        acc)))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1604-1627)
```text
(define-public (liquidate-redeem
                (borrower principal)
                (collateral-ft <ft-trait>)
                (debt-ft <ft-trait>)
                (debt-amount uint)
                (min-collateral-expected uint)
                (min-underlying uint)
                (receiver (optional principal))
                (price-feeds (optional (list 3 (buff 8192)))))
  (let ((coll-address (contract-of collateral-ft))
        (coll-asset (try! (get-asset coll-address)))
        (ztoken-id (get id coll-asset))
        ;; Map zToken to underlying vault ID for redemption
        (underlying-id (if (is-eq ztoken-id zSTX) STX
                       (if (is-eq ztoken-id zsBTC) sBTC
                       (if (is-eq ztoken-id zstSTX) stSTX
                       (if (is-eq ztoken-id zUSDC) USDC
                       (if (is-eq ztoken-id zUSDH) USDH
                       (if (is-eq ztoken-id zstSTXbtc) stSTXbtc
                       u100)))))))  ;; invalid sentinel for non-ztoken
        (funds-receiver (match receiver recv recv contract-caller)))
    
    ;; Validate collateral is a zToken
    (asserts! (is-ztoken ztoken-id) ERR-UNKNOWN-VAULT)
```
