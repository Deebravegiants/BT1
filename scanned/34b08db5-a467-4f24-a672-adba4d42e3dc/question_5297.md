# Q5297: next-index via deposit: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling `min-out`, drive `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) — which returns the stale `index` unchanged when the accrue pause state is set, instead of reverting — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `deposit` call, then the attacker-shaped one with `min-out`, and assert the attacker's net token balance change is zero or negative.
