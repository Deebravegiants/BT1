# Q2721: resolve-interpolation-points via redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling `recipient`, drive `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) — which selects the bracketing curve points for a utilization — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-interpolation-points` touches, run `redeem` with `recipient`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
