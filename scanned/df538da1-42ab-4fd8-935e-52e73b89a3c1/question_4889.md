# Q4889: calc-principal-ratio-reduction via accrue: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling whether an earlier call in the same block already advanced last-update, drive `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) — which reduces scaled principal proportionally to an amount over total debt — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `accrue` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `accrue` call, then the attacker-shaped one with whether an earlier call in the same block already advanced last-update, and assert the attacker's net token balance change is zero or negative.
