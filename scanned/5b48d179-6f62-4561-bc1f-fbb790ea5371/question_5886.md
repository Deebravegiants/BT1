# Q5886: linear-interpolate via liquidate: credit one side of an accounting pair without the other

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) credit one side of an accounting pair without the other? `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `price-feeds` buffers and their ordering across its boundary values through `liquidate` in simnet and assert `linear-interpolate` never returns a value that breaks the invariant.
