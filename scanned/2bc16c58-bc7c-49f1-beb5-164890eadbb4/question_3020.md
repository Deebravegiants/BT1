# Q3020: iter-lookup-collateral via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls whether this asset is already collateral (the is-new-collateral branch) reach `iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with whether this asset is already collateral (the is-new-collateral branch) varied, and assert that the value `iter-lookup-collateral` returns is identical in both runs; a divergence confirms the finding.
