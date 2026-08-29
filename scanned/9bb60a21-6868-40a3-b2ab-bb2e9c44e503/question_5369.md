# Q5369: accrue via liquidate-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the redemption receiver, drive `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) — which advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:835` -> `accrue`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `accrue` advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale. Reach it through `liquidate-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate-redeem` call, then the attacker-shaped one with the redemption receiver, and assert the attacker's net token balance change is zero or negative.
