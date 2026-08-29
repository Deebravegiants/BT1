# Q0025: get-available-assets via redeem: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling the gap between the `assets` var and the real balance, drive `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) — which reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `redeem` with the gap between the `assets` var and the real balance, then read `get-available-assets` state before and after in the same block and assert the two sides of the invariant are equal.
