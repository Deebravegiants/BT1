# Q2849: total-supply-preview via transfer: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the destination principal, including the market, the market-vault or the treasury, drive `total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) — which adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `transfer` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `transfer` call, then the attacker-shaped one with the destination principal, including the market, the market-vault or the treasury, and assert the attacker's net token balance change is zero or negative.
