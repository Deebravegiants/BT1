# Q2441: total-assets-preview via transfer: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the destination principal, including the market, the market-vault or the treasury, drive `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) — which re-derives a FORWARD index inside calls that have already accrued — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `transfer` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `transfer` call, then the attacker-shaped one with the destination principal, including the market, the market-vault or the treasury, and assert the attacker's net token balance change is zero or negative.
