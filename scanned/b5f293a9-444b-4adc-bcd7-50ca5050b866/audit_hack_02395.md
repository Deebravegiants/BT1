# [M] Interest May Not Compound

## Summary
Severity: Medium
Source: https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CToken.sol#L597
Type: audit-issue

## Details
When calculating interest in [CToken.accrueInterest()](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CToken.sol#L597), simple interest is applied over the blocks since the last update. This will underestimate the amount of interest that would be calculated if it were compounded every block.

The code is designed to accrue interest as frequently as possible, but this requirement expands the responsibility of accruing interest into otherwise unrelated functions. Additionally, the size of the discrepancy between the computed and theoretical interest will depend on the volume of transactions being handled by the Compound protocol, which may change unpredictably.

To improve predictability and functional encapsulation, consider calculating interest with the compound interest formula, rather than simulating it through repeated transactions. Note that the additional gas requirements may be reduced using the [modexp precompile](https://medium.com/@rbkhmrcr/precompiles-solidity-e5d29bd428c4). Separately, consider measuring the time between calls to `accrueInterest()` using _seconds_ rather than _blocks_. This will help keep the interest rate calculation robust against changes to the average blocktime.
