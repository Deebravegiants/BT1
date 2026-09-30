# [M] Incorrect isLiquidationEnabled() Logic

## Summary
Severity: Medium
Contest weight: 0.4083
Dataset id: 11671
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Augmented Finance protocol is in essence an over-collateralized lending pool that has the lending functionality and supports a number of normal lending functionalities for supplying and borrowing users, i.e., mint()/redeem() and borrow()/repay(). In the following, we examine one specific functionality, i.e., liquidation. In particular, the Augmented Finance protocol has abstracted the liquidation and flashloan functionalities as standalone features that can be dynamically turned on or off. To elaborate, we show below the two view routines isFlashLoanEnabled()/isLiquidationEnabled() to query for the current configuration. It comes to our attention that the isLiquidationEnabled() function implements an incorrect logic in evaluating !_flashloanDisabled (line 1060), which should be !_liquidationDisabled.
```solidity
function isFlashLoanEnabled() external view returns (bool) {
    return !_flashloanDisabled;
}

function isLiquidationEnabled() external view returns (bool) {
    return !_flashloanDisabled;
}
```

## Recommendation
Correct the flawed logic of isLiquidationEnabled().
