# Q4590: vault-system-borrow via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `price-feeds` buffers, can an unprivileged attacker make `vault-system-borrow` (mainnet/contracts/market/v0-4-market.clar:198) destroy value through a truncation the opposite operation does not restore? `vault-system-borrow` routes a borrow to one of six vaults by asset id, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:198` -> `vault-system-borrow`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `vault-system-borrow` routes a borrow to one of six vaults by asset id. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers across its boundary values through `borrow` in simnet and assert `vault-system-borrow` never returns a value that breaks the invariant.
