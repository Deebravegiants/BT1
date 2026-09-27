# [M] \[M08\] Interest may compound unpredictably

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
In the Aave protocol, loans’ interest is compounded after relevant “interest accruing” transactions occur (with a difference between fixed-rate and variable-rate loans, reported in [**“\[N02\] Fixed-rate loans may never compound”**](#n02)). Between two such transactions, the system uses a simple interest rate model.

The code is designed to accrue interest as frequently as possible, but this requirement expands the responsibility of accruing interest into otherwise unrelated functions. Additionally, the size of the discrepancy between the computed and theoretical interest will depend on the volume of transactions being handled by the Aave protocol, which may change unpredictably.

To improve predictability and functional encapsulation, consider calculating interest with the compound interest formula, rather than simulating it through repeated transactions. The [modexp precompile](https://medium.com/@rbkhmrcr/precompiles-solidity-e5d29bd428c4) may assist in lowering gas fees. Alternatively, consider informing users that the protocol’s interest rates are merely _estimations_ rather than exact rates.

**Update**: _The Aave team acknowledges this issue:_

> “We acknowledge this issue, as also strictly correlated with N02\. As a result, we will evaluate before the mainnet release what will be the implementation cost and the benefits of switching to a compounded interest rate formula, and eventually modify the implementation accordingly.”
