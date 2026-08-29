# Q0980: total-debt via redeem: count one deposit as backing for two simultaneous claims

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `amount` of shares burned reach `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) in a state where it count one deposit as backing for two simultaneous claims? Given that it computes cumulative debt from `principal-scaled` and `index`, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `amount` of shares burned varied, and assert that the value `total-debt` returns is identical in both runs; a divergence confirms the finding.
