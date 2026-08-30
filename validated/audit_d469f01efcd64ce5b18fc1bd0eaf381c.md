### Title
zToken liquidity index (exchange rate) values outstanding debt as if fully collectible, letting share holders and cross-market borrowers exploit the price gap before `socialize-debt` writes down the loss - (File: mainnet/contracts/vault/v0-vault-usdc.clar)

### Summary
Zest's vault contracts (`v0-vault-usdc.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-usdh.clar`, `v0-vault-ststxbtc.clar`, and their `local-testing` counterparts) issue zTokens whose redemption rate and cross-market oracle price are derived from `total-assets`, which optimistically includes 100% of scaled debt compounded by the borrow index, even for positions that are already deeply underwater and destined for bad-debt socialization. The write-down of that phantom value only happens synchronously inside `socialize-debt`, which is only invoked from `liquidate`/`liquidate-multi` in `v0-4-market.clar` when a liquidator actually acts. Until that liquidation transaction lands, `total-assets`/`lindex` (and therefore `convert-to-assets`, `redeem`, and the `resolve-ztoken` oracle price) reports a value that assumes the doomed debt will be fully repaid. This is directly analogous to the Yearn yToken `pricePerShare` issue: the exchange rate is "fully calculated" (loss-inclusive) only once the loss is declared via a specific privileged-adjacent action (liquidation/`report`), not continuously.

### Finding Description
`total-assets` / `total-assets-preview` in every vault (e.g. `v0-vault-usdc.clar`) compute: [1](#0-0) 

```
(total-debt) = calc-cumulative-debt(principal-scaled, index)   ;; assumes full repayment
(total-assets) = assets + max(total-debt - total-borrowed, 0)  ;; adds "interest" unconditionally
```

`index` (borrow index) keeps compounding via `accrue`, growing `total-debt` regardless of whether the underlying borrower is solvent. The corresponding `lindex` (liquidity index), which prices zTokens both for `convert-to-assets`/`redeem` and for the cross-market oracle callcode resolver (`resolve-ztoken`, referenced in `docs/oracle.md:143-184` and implemented in `v0-4-market.clar`), is not reduced to reflect a borrower default until `socialize-debt` executes: [2](#0-1) 

`socialize-debt` is only reachable through the liquidation path in `v0-4-market.clar`, which requires `no-collateral-left` (i.e. the position has already been fully seized and still has residual debt) before it writes the loss into `lindex`: [3](#0-2) 

Between the moment a position becomes economically insolvent (e.g. sharp collateral price drop making the debt unrecoverable even after seizing 100% of collateral) and the moment someone actually submits `liquidate`, `total-assets`/`lindex` in the debt-asset vault still values that soon-to-be-written-off debt at full nominal value. Any zToken holder in that same vault can call `redeem` at the still-inflated rate as long as `available-assets` (idle underlying) is sufficient: [4](#0-3) 

Because `redeem` only guards on the immediate idle-liquidity balance and the currently-computed (stale, loss-unaware) `convert-to-assets-preview`, it does not prevent early redemptions from capturing a proportionally larger share of real backing than they are entitled to, at the expense of remaining zToken holders and, since zTokens are also used as rehypothecated collateral throughout the protocol (`supply-collateral-add`/`collateral-remove-redeem` in `v0-4-market.clar:1171-1230`), at the expense of the accuracy of collateral valuations elsewhere in the system.

### Impact Explanation
This breaks the core vault identity: `sum(zToken_balances) * lindex/PRECISION` should equal the actually-recoverable underlying assets, but during the window between insolvency and liquidation, `lindex` is inflated by uncollectible debt. Users who redeem in that window extract more underlying than the vault can honestly back, socializing the resulting shortfall onto remaining zToken holders once `socialize-debt` finally marks down `lindex`. Since zTokens are simultaneously used as collateral for borrowing elsewhere in the protocol (via `supply-collateral-add`, `collateral-remove-redeem`, and oracle callcodes `CALLCODE-ZUSDC`, etc.), the same stale, inflated exchange rate also overstates collateral value used to size other borrowers' LTV, risking protocol-wide undercollateralization. This is a protocol-insolvency / theft-of-principal class impact (remaining depositors permanently absorb losses that early redeemers escaped), consistent with Critical impact criteria.

### Likelihood Explanation
The vaults' interest-index math continues to compound "interest" on any open debt regardless of the borrower's actual solvency, so the identity break exists on any large, single-borrower default (a fairly common event in a lending protocol, not an edge case). Exploiting it requires only observing an oracle price move (e.g. sBTC/STX price crash) that is publicly known before someone calls `liquidate`, then calling `redeem` on the affected vault while `available-assets` liquidity is sufficient — no special privileges are required. This is realistic in practice because liquidation is permissionless but not instantaneous, and MEV/monitoring bots or the borrower's associates could redeem shares in the debt-asset vault ahead of the liquidator.

### Recommendation
Short term: incorporate a conservative solvency discount into `total-assets`/`lindex` computation — e.g., mark debt as at-risk (and exclude/haircut its optimistic accrued interest, or freeze `redeem` for the affected vault) once a position crosses the full-liquidation LTV threshold (`LTV-LIQ-FULL`), rather than waiting for `socialize-debt` to fire. Long term: decouple accruing "paper" interest from vaults with known-insolvent borrowers, or require `accrue`/health-check integration so that the liquidity index used both for redemption and for cross-market zToken oracle pricing reflects worst-case recoverable value rather than nominal debt value, closing the front-running window between insolvency and liquidation.

### Proof of Concept
1. Borrower B has a large USDC debt against sBTC collateral in a Zest egroup near `LTV-LIQ-FULL`.
2. sBTC price crashes so that B's position becomes `no-collateral-left`-eligible (total debt exceeds recoverable collateral value even after seizing 100%), but no one has called `liquidate` yet.
3. Attacker (who holds zUSDC, or quickly deposits USDC via `supply-collateral-add`/`deposit`) calls `redeem` on `v0-vault-usdc`. `total-assets`/`convert-to-assets-preview` still values B's full scaled debt (principal * current borrow `index`) as recoverable, so the attacker redeems zUSDC at the pre-loss (inflated) rate, provided `available-assets` (idle USDC) covers it.
4. Later, a liquidator calls `liquidate` on B's position; because `no-collateral-left` is true, `socialize-debt-asset` → vault `socialize-debt` writes down `lindex` proportionally to the now-realized loss.
5. Remaining zUSDC holders who did not redeem in step 3 absorb a larger proportional loss than they would have if the write-down had occurred atomically with the insolvency event, while the attacker exited at the stale, inflated exchange rate.

### Citations

**File:** local-testing/contracts/vault/vault-ststx.clar (L330-350)
```text
;; -- Debt helpers -----------------------------------------------------------

(define-private (total-debt)
  (calc-cumulative-debt (var-get principal-scaled) (var-get index)))

(define-private (debt-preview)
  (calc-cumulative-debt (var-get principal-scaled) (next-index)))

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

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L795-833)
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

;; -- Lending operations -----------------------------------------------------

(define-public (accrue)
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L942-968)
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

    (print {
      action: "socialize-debt",
      caller: contract-caller,
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
