### Title
Deposit rounding of `convert-to-shares-preview` to zero shares allows silent loss of depositor principal - (File: `mainnet/contracts/vault/v0-vault-usdc.clar`, and identical logic in `v0-vault-sbtc.clar`, `v0-vault-stx.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdh.clar`)

### Summary
The report's bug class is: an integer division used to convert a user-owed amount into a discrete unit can round down to zero, causing the user to receive nothing while their principal is still consumed. In the SecondSwap case, `releaseRate = amount / numSteps` rounds to 0 and the vesting amount is lost. The direct analog in the Zest vault contracts is `deposit()`, which computes `inkind = (convert-to-shares-preview amount)` via `mul-div-down amount ts ta` and mints `inkind` shares to the depositor — but unlike `redeem()`, `deposit()` never asserts `inkind > 0`.

### Finding Description
`convert-to-shares-preview` is defined identically in every vault: [1](#0-0) 

It computes `mul-div-down amount ts ta`, which truncates (rounds down). In `deposit()`, the resulting `inkind` (shares to mint) is used directly with no `> 0` assertion: [2](#0-1) 

The only defensive checks are `(asserts! (> amount u0) ERR-AMOUNT-ZERO)` (checks the *input* underlying amount, not the *output* share amount) and `(asserts! (>= inkind min-out) ERR-SLIPPAGE)`. If the caller supplies `min-out` of `0` (the natural default for a "just deposit" call, or any client library that doesn't compute a non-zero minimum), the slippage check passes even when `inkind == 0`. The contract then executes `receive-underlying` (pulling real underlying tokens from the depositor) and `ft-mint? zft inkind recipient` mints zero shares, and `assets` is increased by the full deposited `amount`. The depositor has transferred real value into the vault and received nothing in return — exactly the "amount / count rounds to zero, victim loses value" pattern from the report, just expressed through the shares/assets ratio (`ts/ta`) instead of a step count.

By contrast, `redeem()` in the same contracts does assert the output is non-zero: [3](#0-2) 

showing the protocol is aware that a zero-output conversion is dangerous and guards against it on the redeem path, but the identical hazard on the deposit path (mint side) is unguarded.

### Impact Explanation
This breaks the core share-minting-versus-backing identity that the vault is supposed to preserve: `assets_added == shares_minted * (ta/ts)`. When `inkind` rounds to 0, `assets` increases but `total_supply` (shares) does not, meaning the depositor's principal is absorbed into the vault's backing and redistributed pro-rata to all other existing shareholders — a permanent, uncompensated loss of the depositor's principal. This is a direct theft/freezing-of-principal scenario (principal is not returned in shares nor recoverable), which maps to Critical/High impact per the given classification (permanent loss/freezing of user principal).

### Likelihood Explanation
Likelihood depends on the vault having `ta/ts` (assets-per-share) high enough that a legitimate deposit amount converts to less than 1 share. This occurs naturally over time as interest accrues and shares appreciate in value relative to the underlying (the `ts`/`ta` ratio drifts as `total-assets-preview` grows faster than share supply). For vaults holding low-decimal or high value-per-unit assets (e.g., `v0-vault-sbtc.clar`, 8-decimal sBTC), or after the vault has operated long enough for the share price to inflate materially, small deposits (or deposits from clients that don't set `min-out` conservatively) can trigger this rounding-to-zero condition without any attacker action — purely as a consequence of legitimate value appreciation and truncating division, consistent with the "medium likelihood" the original report assigns to its analogous rounding issue.

### Recommendation
Add an explicit `(asserts! (> inkind u0) ERR-OUTPUT-ZERO)` check in `deposit()` (mirroring the existing check already present in `redeem()`) in all vault contracts (`v0-vault-usdc.clar`, `v0-vault-sbtc.clar`, `v0-vault-stx.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdh.clar`), so that a deposit which would mint zero shares reverts instead of silently consuming the depositor's underlying tokens.

### Proof of Concept
1. Assume vault state such that `ta` (total-assets-preview) and `ts` (total-supply-preview) satisfy `ta > ts` sufficiently (share price > 1 underlying unit per share), e.g. `ta = 2,000,000`, `ts = 1,000,000` (share price = 2).
2. User A calls `deposit(amount=1, min-out=0, recipient=A)`.
3. `convert-to-shares-preview(1)` computes `mul-div-down(1, 1000000, 2000000) = floor(1,000,000/2,000,000) = 0`.
4. `inkind = 0`; the check `(asserts! (>= inkind min-out) ERR-SLIPPAGE)` passes since `0 >= 0`.
5. `receive-underlying(1, A)` pulls 1 unit of underlying from A into the vault.
6. `ft-mint? zft 0 A` mints zero shares to A.
7. `var-set assets (+ current-assets 1)` — the vault's tracked backing increases, but A's share balance is unchanged (0).
8. A has irrevocably lost 1 unit of underlying with no shares to redeem it back — the loss scales linearly with any deposit amount smaller than the current share price threshold. [1](#0-0) [2](#0-1)

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L306-313)
```text
(define-private (convert-to-shares-preview (amount uint))
  (let ((ta (total-assets-preview))
        (ts (total-supply-preview)))
    (if (is-eq ts u0)
        amount
        (if (is-eq ta u0)
            u0
            (mul-div-down amount ts ta)))))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L761-793)
```text
(define-public (deposit (amount uint) (min-out uint) (recipient principal))
    (let (
      (states (var-get pause-states))
      (u (try! (accrue)))
      (account contract-caller)
      (CAP-SUPPLY (var-get cap-supply))
      (current-assets (var-get assets))
      (inkind (convert-to-shares-preview amount)))

    (asserts! (not (get deposit states)) ERR-PAUSED)
    (asserts! (var-get initialized) ERR-INIT)
    (asserts! (not (var-get in-flashloan)) ERR-REENTRANCY)
    (asserts! (> amount u0) ERR-AMOUNT-ZERO)
    (asserts! (>= inkind min-out) ERR-SLIPPAGE)
    (asserts! (<= (+ current-assets amount) CAP-SUPPLY) ERR-SUPPLY-CAP-EXCEEDED)

    (try! (receive-underlying amount account))
    (try! (ft-mint? zft inkind recipient))
    (var-set assets (+ current-assets amount))

    (print {
      action: "deposit",
      caller: contract-caller,
      data: {
        depositor: account,
        recipient: recipient,
        amount: amount,
        shares-minted: inkind,
        assets: (+ current-assets amount)
      }
    })

    (ok inkind)))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L795-810)
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
```
