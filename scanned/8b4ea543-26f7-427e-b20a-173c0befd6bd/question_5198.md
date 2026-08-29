# Q5198: add-user-scaled-debt via liquidate-multi: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling which borrowers are placed early versus late in the batch, can an unprivileged attacker make `add-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:237) count one deposit as backing for two simultaneous claims? `add-user-scaled-debt` adds to the scaled debt row with a graceful u0 default, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:237` -> `add-user-scaled-debt`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `add-user-scaled-debt` adds to the scaled debt row with a graceful u0 default. Reach it through `liquidate-multi` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with which borrowers are placed early versus late in the batch varied, and assert that the value `add-user-scaled-debt` returns is identical in both runs; a divergence confirms the finding.
