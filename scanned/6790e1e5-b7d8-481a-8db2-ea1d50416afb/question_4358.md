# Q4358: calc-utilization via repay: destroy value through a truncation the opposite operation 

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling `on-behalf-of`, naming any third-party principal, can an unprivileged attacker make `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) destroy value through a truncation the opposite operation does not restore? `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `on-behalf-of`, naming any third-party principal varied, and assert that the value `calc-utilization` returns is identical in both runs; a divergence confirms the finding.
