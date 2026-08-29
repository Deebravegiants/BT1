# Q2529: calc-index-next via accrue: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling the utilization the rate is interpolated at, drive `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) — which applies a multiplier to the current index — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `calc-index-next` touches, run `accrue` with the utilization the rate is interpolated at, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
