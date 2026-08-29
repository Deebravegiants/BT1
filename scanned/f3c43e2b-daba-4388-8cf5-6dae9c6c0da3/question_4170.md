# Q4170: linear-interpolate via repay: destroy value through a truncation the opposite operation 

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling `on-behalf-of`, naming any third-party principal, can an unprivileged attacker make `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) destroy value through a truncation the opposite operation does not restore? `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `on-behalf-of`, naming any third-party principal across its boundary values through `repay` in simnet and assert `linear-interpolate` never returns a value that breaks the invariant.
