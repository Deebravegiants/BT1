# Q2966: next-liquidity-index via call-ststx-ratio: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling the block and transaction position at which the external ratio is fetched, can an unprivileged attacker make `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) leave a residue that no reconciliation pass ever inspects? `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `call-ststx-ratio` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with the block and transaction position at which the external ratio is fetched varied, and assert that the value `next-liquidity-index` returns is identical in both runs; a divergence confirms the finding.
