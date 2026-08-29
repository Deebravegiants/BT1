# Q2042: calc-principal-ratio-reduction via transfer: have the same quantity scaled twice by two contracts that 

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling the destination principal, including the market, the market-vault or the treasury, can an unprivileged attacker make `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) have the same quantity scaled twice by two contracts that round differently? `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with the destination principal, including the market, the market-vault or the treasury varied, and assert that the value `calc-principal-ratio-reduction` returns is identical in both runs; a divergence confirms the finding.
