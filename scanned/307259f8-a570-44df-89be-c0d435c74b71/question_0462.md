# Q0462: total-assets via accrue: mint shares whose backing was never received

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling whether an earlier call in the same block already advanced last-update, can an unprivileged attacker make `total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) mint shares whose backing was never received? `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether an earlier call in the same block already advanced last-update across its boundary values through `accrue` in simnet and assert `total-assets` never returns a value that breaks the invariant.
