# Q2195: calc-principal-ratio-reduction via deposit: destroy value through a truncation the opposite operation 

## Question
`calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) reduces scaled principal proportionally to an amount over total debt. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing `min-out`, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `deposit` call, then the attacker-shaped one with `min-out`, and assert the attacker's net token balance change is zero or negative.
