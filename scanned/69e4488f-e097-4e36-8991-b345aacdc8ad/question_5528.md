# Q5528: oracle-timestamp-fresh via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the full batch list and its ordering reach `oracle-timestamp-fresh` (mainnet/contracts/market/v0-4-market.clar:365) in a state where it record a repayment larger than the value actually delivered? Given that it sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:365` -> `oracle-timestamp-fresh`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `oracle-timestamp-fresh` sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the full batch list and its ordering varied, and assert that the value `oracle-timestamp-fresh` returns is identical in both runs; a divergence confirms the finding.
