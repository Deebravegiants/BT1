# Q3648: get-asset-value via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `min-collateral-expected` reach `get-asset-value` (mainnet/contracts/market/v0-4-market.clar:679) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:679` -> `get-asset-value`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `get-asset-value` resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `min-collateral-expected` across its boundary values through `liquidate` in simnet and assert `get-asset-value` never returns a value that breaks the invariant.
