# Q0378: add-user-scaled-debt via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `add-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:237) mint shares whose backing was never received? `add-user-scaled-debt` adds to the scaled debt row with a graceful u0 default, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:237` -> `add-user-scaled-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `add-user-scaled-debt` adds to the scaled debt row with a graceful u0 default. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers and their ordering across its boundary values through `liquidate` in simnet and assert `add-user-scaled-debt` never returns a value that breaks the invariant.
