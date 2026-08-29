# Q3623: resolve-interpolation-points via call-ststx-ratio: count one deposit as backing for two simultaneous claims

## Question
`resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) selects the bracketing curve points for a utilization. Can an unprivileged caller of `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), by choosing whether the ratio is fetched before or after other state changes in the block, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `call-ststx-ratio` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `call-ststx-ratio` call, then the attacker-shaped one with whether the ratio is fetched before or after other state changes in the block, and assert the attacker's net token balance change is zero or negative.
