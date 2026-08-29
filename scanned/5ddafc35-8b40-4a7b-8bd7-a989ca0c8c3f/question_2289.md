# Q2289: convert-to-assets-preview via redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling `amount` of shares burned, drive `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) — which prices a redemption against `total-assets-preview` and `total-supply-preview` — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `convert-to-assets-preview` touches, run `redeem` with `amount` of shares burned, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
