# [M] Missing initialization checks and setters for critical parameters of maxExitFee and maxTimelockDuration

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-pooltogether
Published: 2021-06-23
Source: https://github.com/code-423n4/2021-06-pooltogether-findings/issues/49
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

maxExitFee and maxTimelockDuration are critical parameters that impact the UX and prize rewards for users. They are initialized once in initialize() without any sanity/threshold checks and also lack any setters for modifying their values later in case of incorrect initializations or required modifications based on UX.

The lack of setters for post-deployment modifications is to prevent malicious pool owners from increasing the fees or duration on users but this also prevents fixing incorrect initializations requiring expensive contract redeployments.

Impact: Pool owner accidentally set too high/low values. Given the absence of threshold checks or setters, the owner has to redeploy the pool with correct values.


## Proof of Concept

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L182-L187

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L236-L237

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L355

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L723-L724


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Add reasonable sanity/threshold checks in initialize() for these two parameters and evaluate the use of setters that allow modifications with a timelock (advance warning to users) or only with the ability to reduce/increase the values as appropriate.
