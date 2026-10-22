# [M] It is impossible to bridge USDC via CCTPManager

## Summary
Severity: Medium
Contest weight: 0.5695
Dataset id: 22807
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Attempts to bridge USDC after swapping via CCTPManager will revert if the fee token is USDC.
At the start of takeTokensAndTrade for both paymaster contracts, we validate that the fee token is either the input token of the first operation or the output token of the last operation (for Maradona, we check for ETH since the input is always ETH).
dit-v1/contracts/Paymaster/Messi.sol#L89-L91
```solidity
function validateFeeToken(address feeTokenAddress, OperationParameters[] memory ops) internal pure returns (bool) {
    return (feeTokenAddress == ops[0].inputToken || feeTokenAddress == ops[ops.length - 1].outputToken);
}
```
If we're bridging USDC after swapping to USDC tokens and the fee token is USDC, the output token of the bridge op must be USDC due to this check since the bridge op is always last (implies we're paying fees with the output USDC). If we're using CCTPManager, the issue is the output token must be address(0).
dit-v1/contracts/CCTP/CCTPManager.sol#L109
```solidity
require(opParams.outputToken == address(0), "CCTPManager: invalid output token");
```
This contradicts the necessity of setting the output token to USDC to satisfy the original validation against the fee token.
It is impossible to bridge USDC after swapping via CCTPManager if the fee token is USDC due to over-restrictive validation of outputToken in CCTPManager.

## Recommendation
Remove the check on outputToken in CCTPManager.
