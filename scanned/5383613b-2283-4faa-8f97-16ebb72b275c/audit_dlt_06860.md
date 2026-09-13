# [H] Unused slippage params

## Summary
Severity: High
Chain: Smart contract
Component: 2021-11-vader
Published: 2021-11-15
Source: https://github.com/code-423n4/2021-11-vader-findings/issues/253
Type: code-finding

## Details
# Handle

pauliax


# Vulnerability details

## Impact
Unused slippage params.
function addLiquidity in VaderRouter (both V1 and V2) do not use slippage parameters:
```solidity
 uint256, // amountAMin = unused
 uint256, // amountBMin = unused
```
making it susceptible to sandwich attacks / MEV.
For a more detailed explanation, see: https://github.com/code-423n4/2021-09-bvecvx-findings/issues/57

## Recommended Mitigation Steps
Consider paying some attention to the slippage to reduce possible manipulation attacks from mempool snipers.
