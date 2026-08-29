# Q4194: interest-rate via call-ststx-ratio: destroy value through a truncation the opposite operation 

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling whether the ratio is fetched before or after other state changes in the block, can an unprivileged attacker make `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) destroy value through a truncation the opposite operation does not restore? `interest-rate` interpolates the packed curve at the current utilization, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `call-ststx-ratio` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz whether the ratio is fetched before or after other state changes in the block across its boundary values through `call-ststx-ratio` in simnet and assert `interest-rate` never returns a value that breaks the invariant.
