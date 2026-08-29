# Q0973: calc-principal-ratio-reduction via accrue: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling the block time at which accrual is first triggered in a block, drive `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) — which reduces scaled principal proportionally to an amount over total debt — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `accrue` with the block time at which accrual is first triggered in a block, then read `calc-principal-ratio-reduction` state before and after in the same block and assert the two sides of the invariant are equal.
