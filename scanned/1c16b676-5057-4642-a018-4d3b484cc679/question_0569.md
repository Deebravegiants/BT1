# Q0569: system-borrow via repay: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling `amount`, including far above the real debt (the capping path), drive `system-borrow` (mainnet/contracts/vault/v0-vault-stx.clar:865) — which independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:865` -> `system-borrow`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `system-borrow` independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow. Reach it through `repay` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `repay` call, then the attacker-shaped one with `amount`, including far above the real debt (the capping path), and assert the attacker's net token balance change is zero or negative.
