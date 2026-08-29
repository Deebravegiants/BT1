# Q2459: ubalance via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
`ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the seized zToken amount that is immediately redeemed, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate-redeem` call, then the attacker-shaped one with the seized zToken amount that is immediately redeemed, and assert the attacker's net token balance change is zero or negative.
