# [M] Insufficient input validation

## Summary
Severity: Medium
Contest weight: 0.5402
Dataset id: 10544
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are a couple of instances where the functions input params are missing a proper validation. It's okay
that these functions are only callable by the owner but if we have a malicious or compromised owner there
might be a serious problem.
Example is:
```solidity
function updateFees(uint256 _fee) external onlyOwner {
    buyFees = _fee;
    sellFees = _fee;
}
```
Make the same validations for the following functions as well:
updateSwapTokensAtAmount()
updateBuyFees()
updateSellFees()

## Recommendation
Add sensible constraints and validations for all user input mentioned above. Example for updateFees():
```solidity
require(_fee <= 100 && _fee > 0, "New fee is out of boundaries");
```
