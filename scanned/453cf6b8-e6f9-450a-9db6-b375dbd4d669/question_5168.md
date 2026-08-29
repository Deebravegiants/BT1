# Q5168: status-multi via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `status-multi` (mainnet/contracts/registry/v0-assets.clar:163) in a state where it record a repayment larger than the value actually delivered? Given that it calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:163` -> `status-multi`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `status-multi` calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `amount` varied, and assert that the value `status-multi` returns is identical in both runs; a divergence confirms the finding.
