# Q0014: vault-system-borrow via repay: mint shares whose backing was never received

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling `on-behalf-of`, naming any third-party principal, can an unprivileged attacker make `vault-system-borrow` (mainnet/contracts/market/v0-4-market.clar:198) mint shares whose backing was never received? `vault-system-borrow` routes a borrow to one of six vaults by asset id, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:198` -> `vault-system-borrow`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `vault-system-borrow` routes a borrow to one of six vaults by asset id. Reach it through `repay` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `on-behalf-of`, naming any third-party principal varied, and assert that the value `vault-system-borrow` returns is identical in both runs; a divergence confirms the finding.
