# Q5537: send-underlying via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `min-underlying`, drive `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) — which pushes the underlying under an `as-contract?` post-condition scope — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with `min-underlying`, and assert the attacker's net token balance change is zero or negative.
