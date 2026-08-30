### Title
Vault depositors can frontrun bad-debt socialization to redeem zTokens at a stale (pre-writedown) exchange rate, shifting losses onto remaining holders - ([File: mainnet/contracts/vault/v0-vault-usdc.clar], [File: mainnet/contracts/market/v0-4-market.clar])

### Summary
Zest's vault "liquidity index" (`lindex`) determines the exchange rate between zTokens and their underlying asset, and it can be written **down** when a borrower's debt is socialized as bad debt during liquidation. Because this writedown only happens atomically when `liquidate` is actually called, any zToken holder who observes an about-to-be-liquidated, undercollateralized/insolvent position can frontrun the liquidator's transaction by calling `redeem` first, extracting their share of the underlying at the old, inflated `lindex` before the loss is applied. This is the same bug class as the Napier `H-2` report — a value drop known in advance (there, LST/LRT price loss; here, bad-debt writedown) can be dodged by racing the on-chain event that finalizes it, at the expense of the users who remain.

### Finding Description
The vault's exchange rate is `lindex`, used in `convert-to-assets-preview` to compute how many underlying tokens a `redeem` call returns for a given amount of zTokens [1](#0-0) .

When a borrower is liquidated and has no collateral left to cover their debt, `market.clar`/`v0-4-market.clar` performs bad-debt socialization by calling the vault's `socialize-debt`, which writes `lindex` **down** proportionally to the loss in total assets [2](#0-1) : [3](#0-2) 

Until that `liquidate`/`socialize-debt` transaction lands, the vault's `lindex` still reflects the *old, inflated* book value that includes the uncollectible debt as if it were still fully performing. A borrower's position (collateral, debt, health) is fully public on-chain, so any market participant can detect that a position is insolvent (has no collateral left to seize, i.e., will trigger `no-collateral-left` bad-debt socialization) before a liquidator's `liquidate` call is confirmed [4](#0-3) .

An attacker (or any informed zToken holder) can then submit a `redeem` call with higher priority than the pending `liquidate` transaction. Because `redeem` only checks that the vault currently holds enough liquid `available-assets`/`current-assets` (not yet reduced by the future writedown) [5](#0-4) , the redemption succeeds at the stale, higher `lindex`, extracting full value. Once the frontrunning `redeem` is mined first, `socialize-debt` executes afterward and re-distributes the same absolute bad-debt loss across a now-smaller pool of remaining zToken holders, i.e., the identity

```
sum(zToken_i * lindex) == total_assets + total_borrowed (before bad debt)
```

is broken in favor of the redeemer: the redeemer extracts `zToken_amount * lindex_stale`, while the loss that should have been split pro-rata across all zToken holders (including the redeemer) is instead absorbed entirely by those who stayed.

### Impact Explanation
This lets an informed depositor avoid their pro-rata share of a bad-debt loss by racing the liquidation transaction that finalizes the writedown, directly transferring value from remaining zToken holders to the redeemer. This is a direct loss of principal for the users who did not (or could not) redeem in time — a theft of user funds via socialized bad debt, matching the "theft of user funds at rest" / partial protocol insolvency criteria.

### Likelihood Explanation
Liquidations and the underlying positions (collateral, debt, oracle prices) are fully observable on-chain, and the moment a position has "no collateral left" is deterministic and predictable before the `liquidate` call actually lands. Any zToken holder running a bot that monitors positions and mempool for pending liquidations of insolvent (undercollateralized/underwater) borrowers can exploit this with a simple `redeem` transaction using transaction-fee prioritization — no special privileges or complex conditions are required, mirroring the "monitor + frontrun" pattern in the referenced report.

### Recommendation
Decouple bad-debt recognition from the discrete `liquidate` call: continuously (or lazily, on every `accrue`) mark debt on positions with `no-collateral-left`/negative-equity conditions as bad debt and reflect the pending writedown in `lindex`/`convert-to-assets-preview` immediately once a position becomes provably insolvent, rather than only at the moment `liquidate` executes. Alternatively, introduce a withdrawal queue or short redemption delay for vault redemptions so that a `redeem` cannot be finalized ahead of a bad-debt event that is already knowable on-chain, consistent with the report's own recommended mitigation.

### Proof of Concept
1. Borrower `B` has an undercollateralized position in `vault-usdc` such that collateral value has fallen to (or below) zero relative to debt — publicly visible via `market.clar`/`market-vault.clar` state.
2. Liquidator `L` submits `liquidate(B, ...)`, which will call `socialize-debt-asset` → `vault-usdc.socialize-debt`, writing `lindex` down [3](#0-2) .
3. Attacker `A`, holding `zUSDC`, observes `L`'s pending transaction in the mempool (or simply detects the insolvent position independently) and submits `redeem(amount, min-out, A)` with a higher fee/priority.
4. `A`'s `redeem` is mined first, computing `inkind` via the still-inflated `lindex` and paying out full value from `current-assets` [5](#0-4) .
5. `L`'s `liquidate` then executes, calling `socialize-debt` which now spreads the same absolute bad-debt loss over a smaller remaining zToken supply (and reduced `assets`), reducing `lindex` more sharply for everyone who did not redeem in time [6](#0-5) .
6. `A` has avoided the loss entirely; remaining zToken holders now bear a larger-than-fair share of the bad debt.

Note: I could not fully verify within the available context whether any additional safeguard (e.g., a global pause, grace period, or oracle-driven health check invoked inside `redeem` itself) exists elsewhere in `market.clar` that might restrict `redeem` during an active liquidation window; the vault-level `redeem` function itself, as shown, only checks liquidity/pause state and does not reference the borrower's pending liquidation status.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L795-817)
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
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L942-965)
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

**File:** mainnet/contracts/market/v0-4-market.clar (L879-903)
```text
(define-private (socialize-debt-asset
                (debt-entry { aid: uint, scaled: uint })
                (acc { borrower: principal, success: bool }))
  ;; Early return if previous socialization failed
  (if (not (get success acc))
      acc
      (let ((borrower (get borrower acc))
            (failed-status { borrower: borrower, success: false })
            (asset-id (get aid debt-entry))
            (scaled-debt (get scaled debt-entry)))

            ;; Socialize in vault - pass scaled directly to avoid rounding
            (unwrap! (vault-socialize-debt asset-id scaled-debt) failed-status)
            ;; Refresh cache with new indexes post-write-down (lindex decreased)
            (map-set index-cache
                     { timestamp: stacks-block-time, aid: asset-id }
                     (unwrap! (vault-accrue asset-id) failed-status))
            ;; Remove from obligation
            (unwrap! (contract-call? .v0-market-vault
                                      debt-remove-scaled
                                      borrower
                                      scaled-debt
                                      asset-id) failed-status)
          acc)
        ))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1526-1533)
```text
          (no-collateral-left (and
                                (is-eq coll-removed u0)
                                (or
                                  (is-eq (len (get collateral pos-full)) u1)
                                  (and
                                    (is-eq (len (get collateral pos-full)) (len (get collateral position)))
                                    (is-eq other-debt-repayable u0))))))

```
