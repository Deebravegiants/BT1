# Q4382: calc-utilization via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the order of accrual versus price resolution inside the let, can an unprivileged attacker make `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) destroy value through a truncation the opposite operation does not restore? `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the order of accrual versus price resolution inside the let varied, and assert that the value `calc-utilization` returns is identical in both runs; a divergence confirms the finding.
