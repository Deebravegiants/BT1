# Q0906: remove-user-collateral via collateral-add: mint shares whose backing was never received

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling call ordering within the block, can an unprivileged attacker make `remove-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:205) mint shares whose backing was never received? `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:205` -> `remove-user-collateral`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz call ordering within the block across its boundary values through `collateral-add` in simnet and assert `remove-user-collateral` never returns a value that breaks the invariant.
