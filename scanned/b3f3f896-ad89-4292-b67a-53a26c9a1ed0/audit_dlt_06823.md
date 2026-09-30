# [M] Out of gas.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-12-yetifinance
Published: 2021-12-21
Source: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/151
Type: code-finding

## Details
# Handle

Jujic


# Vulnerability details

There is no upper limit on `poolColl.tokens[]`, it increments each time  when a new collateral is added. Eventually, as the count of collateral increases, gas cost of smart contract calls will raise  and that there is no implemented function to reduce the array size.
## Impact
For every call  `getVC()` function which computed  contain the VC value of a given collateralAddress is listed in `poolColl.tokens[]` array, the gas consumption can be more expensive each time that a new collateral address is appended to the  array, until reaching an "Out of Gas" error or a "Block Gas Limit" in the worst scenario.

## Proof of Concept
https://github.com/code-423n4/2021-12-yetifinance/blob/5f5bf61209b722ba568623d8446111b1ea5cb61c/packages/contracts/contracts/ActivePool.sol#L268

https://github.com/code-423n4/2021-12-yetifinance/blob/5f5bf61209b722ba568623d8446111b1ea5cb61c/packages/contracts/contracts/DefaultPool.sol#L184

## Tools Used
Remix

## Recommended Mitigation Steps
Array's length should be checked.
