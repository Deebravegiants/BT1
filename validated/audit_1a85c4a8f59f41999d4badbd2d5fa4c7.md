### Title
Redeeming zTokens before liquidation-triggered bad-debt socialization lets early redeemers escape losses at the expense of remaining depositors - ([File: mainnet/contracts/vault/v0-vault-stx.clar])

### Summary
Zest vaults compute the zToken exchange rate from `assets` (idle underlying) plus outstanding scaled debt valued at the current borrow `index`, without discounting for debt that has already become uncollectible (borrower undercollateralized/insolvent). The write-down that reflects a real loss only happens inside `liquidate()` → `socialize-debt-asset` → vault `socialize-debt`, which reduces `lindex` (the exchange-rate index) for the whole vault. Between the moment a position becomes bad debt and the moment a liquidator actually executes the full liquidation call that triggers `socialize-debt`, any zToken holder can call `redeem` and cash out at the stale, pre-write-down exchange rate, shifting the entire loss onto zToken holders who redeem after the socialization event — the same fact pattern as the referenced StakeWise report, where depositors frontran the oracle's slashing update to `redeem`/`enterExitQueue` before the loss was posted.

### Finding Description
`redeem()` in each vault (e.g. [1](#0-0) ) burns zft shares and pays out `inkind = convert-to-assets-preview(amount)`, computed from the vault's current `lindex`/`assets`/debt state after calling `accrue()`. `accrue()` only advances the borrow `index`/`lindex` based on time-based interest accrual; it does **not** know whether any position backing that debt is now unrecoverable [2](#0-1) .

The only mechanism that marks debt as bad and writes down the vault's `lindex` (the value that determines the zToken-to-underlying exchange rate) is `socialize-debt`, invoked from the market's liquidation path when a borrower's position has zero collateral left after a liquidation call: [3](#0-2) 
which calls `vault-socialize-debt` → the per-vault `socialize-debt` function: [4](#0-3) 

The equation broken is the share-backing identity:
`total-assets(vault) == idle-assets + sum(collectible-debt)`
must hold at all times for `convert-to-assets-preview` to fairly represent every zToken holder's claim. Instead, in Zest it is:
`total-assets(vault) == idle-assets + sum(scaled-debt * index)`
i.e. debt is valued at face value (principal × accrued index) even after it has become economically worthless (borrower's collateral has already collapsed below the debt, e.g., due to a price crash caught by any market participant watching oracle feeds), right up until a liquidator's `liquidate()` transaction fully closes the position and executes `socialize-debt-asset`. Any depositor who observes the same signal that will trigger liquidation (a price update making a position deeply underwater) can race the liquidator/oracle update and call `redeem()` first, extracting their proportional share at the inflated (pre-write-down) exchange rate. Later redeemers absorb 100% of the loss when `lindex` is subsequently discounted: [5](#0-4) 

### Impact Explanation
This is a temporary/permanent freezing and effective theft-of-principal issue for the zToken holders who do not race to redeem: their principal's backing is silently transferred to the early redeemers because the vault's `lindex` overstates backing until socialization. In the worst case (large bad debt relative to vault TVL, or a vault that becomes fully drained of idle assets by early redeemers) remaining users may be left holding zTokens backed by a shortfall, i.e., partial protocol insolvency for that vault, mirroring the "Charlie bears complete loss individually" outcome in the referenced report.

### Likelihood Explanation
Likelihood is lower than the StakeWise original because Zest liquidations are typically atomic/permissionless and can occur in the same or next block as the price move that causes insolvency (there is no analogous multi-day oracle-report/exit-queue delay). The race window is therefore the time between a price feed update/oracle price movement making a position deeply underwater and the liquidator's `liquidate()` transaction confirming. This window can still be non-trivial (multiple pending price updates, contested liquidator MEV, or a position becoming unliquidatable in one shot due to `ERR-ZERO-LIQUIDATION-AMOUNTS`/slippage checks causing delay across several liquidation calls), giving sophisticated actors a window to redeem idle vault assets ahead of the socialization event, particularly in low-liquidity vaults.

### Recommendation
- Discount face-value debt used in `convert-to-assets-preview`/`total-assets` by an estimate of expected loss for positions that are already known to be undercollateralized (e.g., via a health-factor check against outstanding collateral value) rather than relying solely on the borrow index.
- Alternatively, add a redemption fee/cooldown, or pause `redeem` for a vault the moment a tracked position's health factor drops below a threshold (before liquidation completes), so exchange-rate write-downs are reflected before withdrawals are allowed to drain idle assets.
- Consider allowing `socialize-debt` to be triggered proactively (permissionlessly) once a position is provably insolvent, independent of a profitable liquidation being executed, to shrink the window during which stale backing can be exploited.

### Proof of Concept
1. Borrower B has an undercollateralized position in vault V (e.g., STX collateral price crashes via a legitimate Pyth update, or interest accrual pushes debt above collateral value) such that liquidation will ultimately leave zero collateral and trigger `socialize-debt-asset` for a nonzero `bad-debt-socialized`.
2. Depositor A observes the same public price feed / position data (via a node or off-chain monitoring of `market.clar`'s state) that will make B's position liquidatable with residual bad debt.
3. Before any liquidator calls `liquidate()` on B (and thus before `socialize-debt` reduces `lindex`), A calls `redeem()` on vault V — see [1](#0-0)  — receiving `inkind` computed at the current (stale) `lindex`, using up available idle `assets`.
4. A liquidator subsequently calls `liquidate()`; since B's position has no collateral left, `socialize-debt-asset` fires [3](#0-2) , calling vault `socialize-debt` which writes down `lindex` proportionally to the loss [5](#0-4) .
5. Remaining zToken holders in V now redeem at the reduced `lindex`, receiving strictly less than A did per share, even though all zToken holders should have shared the loss proportionally.

Note: I was unable to fully verify the exact liquidation-bot response latency/atomicity assumptions on the Stacks network (e.g., typical block time and whether liquidations are reliably executed same-block), which affects the practical size of the race window and therefore the realistic likelihood of this analog; this uncertainty should be validated further (e.g., via a Devin session running the local-testing Vitest suite) before treating the likelihood as high.

### Citations

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L797-831)
```text
(define-public (redeem (amount uint) (min-out uint) (recipient principal))
  (let (
    (states (var-get pause-states))
    (u (try! (accrue)))
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
      redeemer: account,
      recipient: recipient,
      shares-burned: amount,
      amount-received: inkind,
      assets: (- current-assets inkind)
    }
  })

  (ok inkind)))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L835-863)
```text
(define-public (accrue)
  (let ((states (var-get pause-states))
        (idx (var-get index))
        (lidx (var-get lindex)))
      (if (get accrue states)
          ;; PAUSED: Pass-through without reverting
          (ok { index: idx, lindex: lidx })
          ;; NOT PAUSED: Normal accrual logic
          (let ((next (next-index))
                (nliq (next-liquidity-index))
                (scaled-principal (var-get principal-scaled))
                (old-debt (mul-div-down scaled-principal idx INDEX-PRECISION))
                (new-debt (mul-div-down scaled-principal next INDEX-PRECISION))
                (debt-delta (if (> new-debt old-debt) (- new-debt old-debt) u0))
                (reserve-inc (mul-div-down debt-delta (var-get fee-reserve) BPS))
                (treasury-lp (if (> reserve-inc u0) (mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc)) u0)))
            (if (not (is-eq idx next))
                (var-set index next)
                false)
            (if (not (is-eq lidx nliq))
                (var-set lindex nliq)
                false)
            (if (> treasury-lp u0)
                (try! (ft-mint? zft treasury-lp .dao-treasury))
                false)
            (if (or (not (is-eq idx next)) (not (is-eq lidx nliq)))
                (var-set last-update stacks-block-time)
                false)
            (ok { index: next, lindex: nliq })))))
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

**File:** mainnet/contracts/market/v0-4-market.clar (L1534-1560)
```text
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
