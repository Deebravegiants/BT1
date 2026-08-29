# Q0641: debt-preview via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the seized zToken amount that is immediately redeemed, drive `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) — which computes cumulative debt from `principal-scaled` and the FORWARD index — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate-redeem` call, then the attacker-shaped one with the seized zToken amount that is immediately redeemed, and assert the attacker's net token balance change is zero or negative.
