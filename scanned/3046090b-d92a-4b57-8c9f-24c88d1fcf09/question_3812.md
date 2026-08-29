# Q3812: oracle-price-legal via liquidate-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the vault whose share price the redemption moves reach `oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it accepts any price strictly greater than zero, with no upper bound and no sanity band, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `liquidate-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the vault whose share price the redemption moves varied, and assert that the value `oracle-price-legal` returns is identical in both runs; a divergence confirms the finding.
