# Q5714: mask-to-list-internal via borrow: count one deposit as backing for two simultaneous claims

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) count one deposit as backing for two simultaneous claims? `mask-to-list-internal` expands mask bits into a list bounded at 64 entries, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `amount` varied, and assert that the value `mask-to-list-internal` returns is identical in both runs; a divergence confirms the finding.
