# Q1116: principal-ratio-reduction via transfer: count one deposit as backing for two simultaneous claims

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:406) in a state where it count one deposit as backing for two simultaneous claims? Given that it derives a principal reduction from an amount, the scaled principal and the previewed debt, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:406` -> `principal-ratio-reduction`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the destination principal, including the market, the market-vault or the treasury across its boundary values through `transfer` in simnet and assert `principal-ratio-reduction` never returns a value that breaks the invariant.
