# [M] withdrawAssets will always revert

## Summary
Severity: Medium
Contest weight: 0.5587
Dataset id: 15765
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While the contract is not expected to receive any assets, the withdrawAssets function is provided to allow the admin to withdraw any assets that the contract may have received, presumably by mistake.  
withdrawAssets uses the fromStage modifier to ensure that the contract is in the Completed stage.  
```solidity
function withdrawAssets(address recipient, IERC20 asset)
    external
    onlyRole(ADMIN_ROLE)
    fromStage(Stages.Completed)
```
However, this modifier reverts when the current stage is Completed.  
```solidity
modifier fromStage(Stages _requiredStage) {
    Stages _currentStage = getCurrentStage();
    // comingSoon = 0, onlyKyc = 1, tokenPurchase = 2, completed = 3
    if (_requiredStage > _currentStage || _currentStage == Stages.Completed) {
        revert WrongStage(msg.sig, _currentStage, _requiredStage);
    }
}
```
This means that withdrawAssets will always revert

## Recommendation
```diff
function withdrawAssets(address recipient, IERC20 asset)
    external
    onlyRole(ADMIN_ROLE)
-   fromStage(Stages.Completed)
+   {
+       Stages _currentStage = getCurrentStage();
+       if (_currentStage != Stages.Completed) {
+           revert WrongStage(msg.sig, _currentStage, Stages.Completed);
+       }
+       uint256 contractBalance = asset.balanceOf(address(this));
```
