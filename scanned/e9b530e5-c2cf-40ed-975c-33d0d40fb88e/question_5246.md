# Q5246: normalize via liquidate-multi: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling which borrowers are placed early versus late in the batch, can an unprivileged attacker make `normalize` (mainnet/contracts/market/v0-4-market.clar:576) count one deposit as backing for two simultaneous claims? `normalize` divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:576` -> `normalize`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `normalize` divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar. Reach it through `liquidate-multi` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with which borrowers are placed early versus late in the batch varied, and assert that the value `normalize` returns is identical in both runs; a divergence confirms the finding.
