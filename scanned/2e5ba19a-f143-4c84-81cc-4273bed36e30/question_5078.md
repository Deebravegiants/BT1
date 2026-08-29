# Q5078: filter-u128 via borrow: count one deposit as backing for two simultaneous claims

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `filter-u128` (mainnet/contracts/registry/v0-egroup.clar:97) count one deposit as backing for two simultaneous claims? `filter-u128` filters a 128-entry bucket list, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:97` -> `filter-u128`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `filter-u128` filters a 128-entry bucket list. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `amount` varied, and assert that the value `filter-u128` returns is identical in both runs; a divergence confirms the finding.
