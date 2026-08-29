# Q5249: interpolate-rate via repay: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling `on-behalf-of`, naming any third-party principal, drive `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) — which interpolates between packed u16 curve points — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `repay` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `repay` call, then the attacker-shaped one with `on-behalf-of`, naming any third-party principal, and assert the attacker's net token balance change is zero or negative.
