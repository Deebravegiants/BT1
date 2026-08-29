# Q3608: oracle-price-legal via call-ststx-ratio: make the per-user ledger and the vault aggregate disagree 

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls the block and transaction position at which the external ratio is fetched reach `oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it accepts any price strictly greater than zero, with no upper bound and no sanity band, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `call-ststx-ratio` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with the block and transaction position at which the external ratio is fetched varied, and assert that the value `oracle-price-legal` returns is identical in both runs; a divergence confirms the finding.
