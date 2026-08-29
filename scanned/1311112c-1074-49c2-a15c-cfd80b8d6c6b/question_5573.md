# Q5573: unpack-u16 via redeem: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling `recipient`, drive `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) — which unpacks eight u16 curve fields from one packed word — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `redeem` call, then the attacker-shaped one with `recipient`, and assert the attacker's net token balance change is zero or negative.
