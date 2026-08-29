# Q0894: next-liquidity-index via accrue: mint shares whose backing was never received

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling whether an earlier call in the same block already advanced last-update, can an unprivileged attacker make `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) mint shares whose backing was never received? `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether an earlier call in the same block already advanced last-update across its boundary values through `accrue` in simnet and assert `next-liquidity-index` never returns a value that breaks the invariant.
