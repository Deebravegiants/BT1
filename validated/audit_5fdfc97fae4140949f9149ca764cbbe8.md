### Title
Depositors can redeem zTokens at a stale, inflated exchange rate before bad debt is socialized, extracting more than their fair share and shifting losses onto remaining holders - (File: mainnet/contracts/vault/v0-vault-usdc.clar, mainnet/contracts/market/v0-4-market.clar)

### Summary
Zest's zToken vaults compute the exchange rate (`total-assets` / `total-supply`) by adding *all* accrued borrower interest/principal to `assets`, without ever discounting for undercollateralized ("bad debt") positions that have not yet been liquidated. The loss is only written into the liquidity index (`lindex`) at the moment `socialize-debt` is invoked from `liquidate`/`liquidate-multi`. Any zToken holder who calls `redeem` before that discrete write-down transaction executes still redeems at the old, inflated exchange rate, extracting more underlying assets than their fair share and pushing the entire loss onto zToken holders who redeem afterward — the same "harvest gains before distribution / dodge losses before realization" identity break described in the River `OracleManager.setBeaconData` report.

### Finding Description
`total-assets` in the vault contracts is computed as `current-assets + interest`, where `interest` is derived purely from the borrow index and assumes the full outstanding debt (`total-debt`) is recoverable: [1](#0-0) 

This value feeds `convert-to-assets-preview` / `convert-to-shares-preview`, which are used directly by `redeem`: [2](#0-1) 

The exchange rate is therefore optimistic: it never reflects the fact that an underwater borrower's collateral is insufficient to fully back their debt until a liquidator actually calls `liquidate`, and only when `no-collateral-left` triggers `socialize-debt-asset`, does the vault retroactively write down `lindex` (the liquidity index that determines zToken redemption value): [3](#0-2) [4](#0-3) 

The identity that should hold at all times is:
```
totalSupply(zToken) × price(zToken) == totalAssets (recoverable)
```
But because `total-assets`/`total-assets-preview` never subtracts unrealized bad debt from underwater, not-yet-liquidated positions, the equation is broken as:
```
totalSupply × price_stale > totalAssets_actual (recoverable)
```
Any holder redeeming during this window (`price_stale`) receives `shares × price_stale` underlying assets — more than their true pro-rata share of `totalAssets_actual`. Once `socialize-debt` finally executes and marks down `lindex`, the deficit is absorbed entirely by the zToken holders who have not yet redeemed. This precisely mirrors the reported River pattern: "Investors might time their withdrawal/sell lsETH on secondary markets just before the loss is realized... escaping the intended mechanism of socializing losses."

### Impact Explanation
This is a redistribution of realized bad debt from early redeemers onto remaining zToken holders — a break of the share-price/backing identity that can lead to insolvency for the remaining vault depositors (they cannot recover full value for their shares because assets have already been extracted at an inflated rate by earlier redeemers). Given Zest's design intentionally batches liquidation write-downs into a single discrete transaction (`socialize-debt`) rather than continuously marking positions to their recoverable value, any period between a position becoming bad-debt-eligible (fully underwater, e.g. via price crash) and the liquidation transaction confirming is an exploitable window.

### Likelihood Explanation
Underwater/undercollateralized positions and pending liquidations are fully visible on-chain (position health, collateral, prices are all public reads). Any zToken holder monitoring the market can detect an impending bad-debt liquidation (e.g., after a collateral price crash makes a position's debt exceed its collateral value) and submit a `redeem` call before the liquidator's `liquidate` transaction confirms and writes down `lindex`. This requires no privileged access, no oracle manipulation, and no flashloan — only observing public on-chain state and racing a normal `redeem` transaction ahead of the socialization event, exactly as flagged as a valid Medium-risk concern in the source report.

### Recommendation
Discount `total-assets`/`total-assets-preview` for the expected shortfall of known-underwater positions (i.e., mark-to-market the debt side using current oracle prices rather than assuming full recoverability based purely on the borrow index), or introduce a mechanism (e.g., withdrawal queuing/cooldown or a socialized-loss reserve) that prevents redeemers from extracting value at a rate that has not yet accounted for identified bad debt.

### Proof of Concept
1. Attacker (or any zToken holder) monitors the market and observes Borrower B's position: collateral value has dropped (oracle price crash) such that `debt > collateral`, satisfying `no-collateral-left` conditions once liquidated.
2. Before any liquidator calls `liquidate`/`liquidate-multi` (mainnet/contracts/market/v0-4-market.clar `liquidate`), the attacker calls `redeem` on the relevant vault (e.g. `v0-vault-usdc.clar`). `accrue` runs first but does not know about B's shortfall, so `convert-to-assets-preview` still uses the stale, fully-collateralized-assumption exchange rate.
3. Attacker receives `shares × price_stale` in underlying assets, more than their true share of recoverable assets.
4. Later, a liquidator calls `liquidate`, triggering `socialize-debt-asset` → `socialize-debt`, which writes down `lindex` proportionally against the *now-smaller* remaining `total-assets`, meaning the full loss is absorbed disproportionately by the zToken holders who did not redeem in step 2.

### Citations

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L334-346)
```text
(define-private (total-assets)
  (let ((current-assets (var-get assets))
        (debt (total-debt))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))

(define-private (total-assets-preview)
  (let ((current-assets (var-get assets))
        (debt (debt-preview))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L944-967)
```text
(define-public (socialize-debt (scaled-amount uint))
  (let ((scaled-principal (var-get principal-scaled))
        (borrowed (var-get total-borrowed))
        (idx (var-get index))
        (current-assets (var-get assets))
        (current-lindex (var-get lindex))
        (old-total-assets (total-assets))
        (debt-reduction (mul-div-down scaled-amount idx INDEX-PRECISION))
        (principal-reduction (if (> scaled-principal u0)
                                (mul-div-down scaled-amount borrowed scaled-principal)
                                u0))
        ;; Write down lindex proportionally to loss in total-assets
        (new-lindex (if (and (> old-total-assets u0) (> old-total-assets debt-reduction))
                       (mul-div-down current-lindex (- old-total-assets debt-reduction) old-total-assets)
                       u0)))

    (try! (check-caller-auth))
    (asserts! (> scaled-amount u0) ERR-AMOUNT-ZERO)

    (var-set lindex new-lindex)
    (var-set principal-scaled (if (> scaled-principal scaled-amount) (- scaled-principal scaled-amount) u0))
    (var-set total-borrowed (if (> borrowed principal-reduction) (- borrowed principal-reduction) u0))
    (var-set assets (if (> current-assets principal-reduction) (- current-assets principal-reduction) u0))

```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L799-820)
```text
    (account contract-caller)
    (current-assets (var-get assets))
    (balance (get-balance-internal account))
    (balance-check (asserts! (>= balance amount) ERR-INSUFFICIENT-BALANCE))
    (available-assets (get-available-assets))
    (inkind (convert-to-assets-preview amount)))

  (asserts! (>= current-assets inkind) ERR-INSUFFICIENT-ASSETS)
  (asserts! (not (get redeem states)) ERR-PAUSED)
  (asserts! (> amount u0) ERR-AMOUNT-ZERO)
  (asserts! (> inkind u0) ERR-OUTPUT-ZERO)
  (asserts! (>= inkind min-out) ERR-SLIPPAGE)
  (asserts! (>= available-assets inkind) ERR-INSUFFICIENT-LIQUIDITY)

  (try! (ft-burn? zft amount account))
  (try! (send-underlying inkind recipient))
  (var-set assets (- current-assets inkind))

  (print {
    action: "redeem",
    caller: contract-caller,
    data: {
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
