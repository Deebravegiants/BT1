# Q4677: add-user-collateral via repay: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling `amount`, including far above the real debt (the capping path), drive `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) — which adds to the collateral row with a graceful u0 default — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `add-user-collateral` touches, run `repay` with `amount`, including far above the real debt (the capping path), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
