# Q2786: total-debt via transfer: have the same quantity scaled twice by two contracts that 

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling the destination principal, including the market, the market-vault or the treasury, can an unprivileged attacker make `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) have the same quantity scaled twice by two contracts that round differently? `total-debt` computes cumulative debt from `principal-scaled` and `index`, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with the destination principal, including the market, the market-vault or the treasury varied, and assert that the value `total-debt` returns is identical in both runs; a divergence confirms the finding.
