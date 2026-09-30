# [M] FeeLib calculations can revert

## Summary
Severity: Medium
Contest weight: 0.1109
Dataset id: 4186
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FeeLib library is based on the Uniswap's V3 PositionValue library.
However, it is not taken into account that the fee calculations expect overflows and underflows. This is not an issue in the original library, as it uses a solc version lower than 0.8.0, which does not revert to overflow/underflow. But in the Burve implementation, this will cause the transaction to revert.
The issue can be reproduced by running the test_QueryValue_V3_NoFees test on a fork of the Berachain network:
```bash
forge test --mt test_QueryValue_V3_NoFees --fork-url https://rpc.berachain.com/
// --fork-block-number 2073480
```
As a result, all the query functions in Burve.sol might revert unexpectedly.

## Recommendation
Adapt the FeeLib library to use unchecked math operations, allowing the library to handle overflows and underflows without reverting the transaction.
