# [H] Unused slippage params

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

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
