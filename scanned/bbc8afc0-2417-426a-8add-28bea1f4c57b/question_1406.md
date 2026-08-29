# Q1406: oracle-timestamp-fresh via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `min-underlying`, can an unprivileged attacker make `oracle-timestamp-fresh` (mainnet/contracts/market/v0-4-market.clar:365) record a repayment larger than the value actually delivered? `oracle-timestamp-fresh` sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:365` -> `oracle-timestamp-fresh`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `oracle-timestamp-fresh` sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `min-underlying` varied, and assert that the value `oracle-timestamp-fresh` returns is identical in both runs; a divergence confirms the finding.
