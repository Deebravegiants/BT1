# Q2913: receive-underlying via transfer: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling `amount`, drive `receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) — which pulls the underlying from a named account — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `transfer` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `receive-underlying` touches, run `transfer` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
