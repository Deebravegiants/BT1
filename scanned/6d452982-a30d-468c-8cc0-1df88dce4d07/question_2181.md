# Q2181: send-underlying via redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling `recipient`, drive `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) — which pushes the underlying under an `as-contract?` post-condition scope — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `send-underlying` touches, run `redeem` with `recipient`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
