# Q4314: send-tokens via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling whether the position has any enabled debt row (the has-debt branch), can an unprivileged attacker make `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) destroy value through a truncation the opposite operation does not restore? `send-tokens` pushes an asset to a caller-chosen recipient principal, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the position has any enabled debt row (the has-debt branch) across its boundary values through `collateral-remove` in simnet and assert `send-tokens` never returns a value that breaks the invariant.
