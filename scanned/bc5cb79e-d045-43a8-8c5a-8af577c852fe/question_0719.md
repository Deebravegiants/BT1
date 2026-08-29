# Q0719: debt-remove-scaled via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
`debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) clears the debt bit only when the remaining scaled debt is exactly zero. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing the `price-feeds` buffers, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `collateral-remove` call, then the attacker-shaped one with the `price-feeds` buffers, and assert the attacker's net token balance change is zero or negative.
