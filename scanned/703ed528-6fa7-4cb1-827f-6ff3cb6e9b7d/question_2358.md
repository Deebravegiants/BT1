# Q2358: total-supply-preview via redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the gap between the `assets` var and the real balance, can an unprivileged attacker make `total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) have the same quantity scaled twice by two contracts that round differently? `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the gap between the `assets` var and the real balance across its boundary values through `redeem` in simnet and assert `total-supply-preview` never returns a value that breaks the invariant.
