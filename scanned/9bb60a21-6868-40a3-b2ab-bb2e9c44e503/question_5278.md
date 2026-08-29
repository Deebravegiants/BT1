# Q5278: calc-multiplier-delta via deposit: count one deposit as backing for two simultaneous claims

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `recipient`, including a contract principal, can an unprivileged attacker make `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) count one deposit as backing for two simultaneous claims? `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `deposit` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `deposit` with `recipient`, including a contract principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
