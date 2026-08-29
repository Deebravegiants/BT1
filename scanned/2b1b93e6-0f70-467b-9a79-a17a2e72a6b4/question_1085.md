# Q1085: create via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `amount`, drive `create` (mainnet/contracts/market/v0-market-vault.clar:150) — which binds a principal to a fresh numeric id — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
