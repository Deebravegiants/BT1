[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L460-461)
```text
(define-private (get-egroup (mask uint))
  (contract-call? .v0-egroup resolve mask))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1226-1234)
```text
    ;; Step 1: Remove collateral - sends zTokens to THIS contract (market)
    ;; receiver=current-contract so market holds the zTokens
    (try! (collateral-remove ft amount (some current-contract) price-feeds))
    
    ;; Step 2: Redeem zTokens for underlying
    ;; vault-redeem calls vault.redeem which burns shares from contract-caller (market)
    ;; Since market now holds the zTokens, this succeeds
    ;; Underlying tokens are sent to the specified receiver
    (vault-redeem underlying-id amount min-underlying funds-receiver)))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1261-1287)
```text
        (current-group (try! (get-egroup mask)))
        (current-ltvb (buff-to-uint-be (get LTV-BORROW current-group)))

        ;; LTV
        (notional-valued-assets (get-notional-evaluation { position: position, assets: assets }))
        (collateral-value (get collateral notional-valued-assets))
        (debt-value (get debt notional-valued-assets)))

    ;; preconditions
    (asserts! (> amount u0) ERR-AMOUNT-ZERO)
    (asserts! (get debt asset) ERR-BORROW-DISABLED)
    (asserts! (is-healthy collateral-value debt-value current-ltvb) ERR-UNHEALTHY)

    ;; Calculate FUTURE debt (after adding this debt)
    ;; For debt: bit position = asset-id + 64 (DEBT-OFFSET)
    (let ((future-mask (bit-or mask (pow u2 (+ asset-id DEBT-OFFSET))))
          (future-group (try! (get-egroup future-mask)))
          ;; Per-egroup borrow disable check (uses FUTURE egroup, not current)
          ;; Each bit in BORROW-DISABLED-MASK corresponds to a debt asset ID (NOT offset by 64)
          (disabled-borrow-mask (get BORROW-DISABLED-MASK future-group))
          (debt-increase (try! (get-asset-value asset amount true)))
          (debt-post-increased (+ debt-value debt-increase)))

    ;; Check if this specific asset is disabled for borrowing in the FUTURE egroup
    (asserts! (is-eq (bit-and disabled-borrow-mask (pow u2 asset-id)) u0) ERR-EGROUP-ASSET-BORROW-DISABLED)
    ;; postconditions
    (asserts! (try! (is-healthy-with-mask collateral-value debt-post-increased future-mask)) ERR-UNHEALTHY)
```
