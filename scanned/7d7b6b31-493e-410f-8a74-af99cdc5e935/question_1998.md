# Q1998: find-superset via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `debt-amount`, can an unprivileged attacker make `find-superset` (mainnet/contracts/registry/v0-egroup.clar:262) have the same quantity scaled twice by two contracts that round differently? `find-superset` returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:262` -> `find-superset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `find-superset` returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `debt-amount` across its boundary values through `liquidate` in simnet and assert `find-superset` never returns a value that breaks the invariant.
