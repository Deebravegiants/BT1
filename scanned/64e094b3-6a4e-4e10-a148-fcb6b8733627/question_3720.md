# Q3720: status via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `min-collateral-expected` reach `status` (mainnet/contracts/registry/v0-assets.clar:115) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it derives `collateral` and `debt` flags from bit tests against whatever mask it was handed, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:115` -> `status`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `status` derives `collateral` and `debt` flags from bit tests against whatever mask it was handed. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `min-collateral-expected` across its boundary values through `liquidate` in simnet and assert `status` never returns a value that breaks the invariant.
