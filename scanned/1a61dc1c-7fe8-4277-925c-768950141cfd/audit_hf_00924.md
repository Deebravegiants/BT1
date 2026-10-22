# [M] tradeTokenMinSupply must not be

## Summary
Severity: Medium
Contest weight: 0.5447
Dataset id: 2785
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating a new token, the creator needs to set the initial supply and the minimum supply. Take note that the minimum supply cannot be zero, otherwise the AMM calculation will not work (divide by zero) and all the ETH that is spent on buying the tokens cannot be transferred to the uniswap position as curves[erc20Address] cannot be paused, making the ETH stuck in the contract.
```solidity
uint256 newX = x - tokenAmount;
// @audit - the newX will be zero, which will not work
uint256 newYScaled = (k * _PRECISION_MULTIPLIER) / newX;
```

## Recommendation
Check that tradeTokenMinSupply is not zero when calling initializeCustomToken() .
```solidity
function initializeCustomToken(
    // ...
) {
    if (tradeTokenInitSupply <= tradeTokenMinSupply) {
        revert TokenFactory_InvalidParams();
    }
    require(tradeTokenMinSupply != 0, "Minimum supply cannot be zero");
    // ...
}
```
