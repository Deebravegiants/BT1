# Q0714: resolve-pyth via collateral-remove: mint shares whose backing was never received

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the set of assets held, can an unprivileged attacker make `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) mint shares whose backing was never received? `resolve-pyth` reads the Pyth storage record for a 32-byte ident, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the set of assets held across its boundary values through `collateral-remove` in simnet and assert `resolve-pyth` never returns a value that breaks the invariant.
