# Q2244: calc-multiplier-delta via call-ststx-ratio: credit one side of an accounting pair without the other

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls whether the ratio is fetched before or after other state changes in the block reach `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) in a state where it credit one side of an accounting pair without the other? Given that it compounds a rate over `time-delta` with a caller-independent rounding flag, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `call-ststx-ratio` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the ratio is fetched before or after other state changes in the block across its boundary values through `call-ststx-ratio` in simnet and assert `calc-multiplier-delta` never returns a value that breaks the invariant.
