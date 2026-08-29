# Q3486: add-user-collateral via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling the zToken/underlying id mapping reached (the u100 sentinel branch), can an unprivileged attacker make `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) leave a residue that no reconciliation pass ever inspects? `add-user-collateral` adds to the collateral row with a graceful u0 default, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the zToken/underlying id mapping reached (the u100 sentinel branch) across its boundary values through `collateral-remove-redeem` in simnet and assert `add-user-collateral` never returns a value that breaks the invariant.
