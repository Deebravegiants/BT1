# Q2591: oracle-timestamp-fresh via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
`oracle-timestamp-fresh` (mainnet/contracts/market/v0-4-market.clar:365) sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing the full batch list and its ordering, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:365` -> `oracle-timestamp-fresh`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `oracle-timestamp-fresh` sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate-multi` call, then the attacker-shaped one with the full batch list and its ordering, and assert the attacker's net token balance change is zero or negative.
