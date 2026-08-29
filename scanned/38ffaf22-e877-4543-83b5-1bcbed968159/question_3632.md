# Q3632: debt-remove-scaled via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls whether this asset is already collateral (the is-new-collateral branch) reach `debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it clears the debt bit only when the remaining scaled debt is exactly zero, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with whether this asset is already collateral (the is-new-collateral branch) varied, and assert that the value `debt-remove-scaled` returns is identical in both runs; a divergence confirms the finding.
