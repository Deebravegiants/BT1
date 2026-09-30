# [M] M-23 | Uniswap Ticks Rounding

## Summary
Severity: Medium
Contest weight: 0.1418
Dataset id: 22193
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Multiple contracts in the system -[V3TwapUtilities](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/twaputils/V3TwapUtilities.sol#L94-L97), [V3AerodromeUtilities](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/twaputils/V3TwapAerodromeUtilities.sol#L96-L99), [UniswapV3SinglePriceOracle](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/oracle/UniswapV3SinglePriceOracle.sol#L60-L63) - fetch the TWAP price of a given asset. When calculating the TWAP, the delta of two CL ticks is divided by a given time period. Since solidity truncates when it divides, for negative ticks the result will be rounded up instead of rounded down resulting in a different price. For reference, see how is this handled in [OracleLibrary](https://github.com/Uniswap/v3-periphery/blob/697c2474757ea89fec12a4e6db16a574fe259610/contracts/libraries/OracleLibrary.sol#L36).

## Recommendation
Implement the same solution as in OracleLibrary
