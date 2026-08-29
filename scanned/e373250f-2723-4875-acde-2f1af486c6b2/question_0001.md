# Q0001: total-debt via redeem: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling `amount` of shares burned, drive `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) — which computes cumulative debt from `principal-scaled` and `index` — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `redeem` with `amount` of shares burned, then read `total-debt` state before and after in the same block and assert the two sides of the invariant are equal.
