# Q2951: vault-system-borrow via repay: count one deposit as backing for two simultaneous claims

## Question
`vault-system-borrow` (mainnet/contracts/market/v0-4-market.clar:198) routes a borrow to one of six vaults by asset id. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing `on-behalf-of`, naming any third-party principal, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:198` -> `vault-system-borrow`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `vault-system-borrow` routes a borrow to one of six vaults by asset id. Reach it through `repay` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `repay` call, then the attacker-shaped one with `on-behalf-of`, naming any third-party principal, and assert the attacker's net token balance change is zero or negative.
