# [M] In the Tranche.sol, there is no

## Summary
Severity: Medium
Contest weight: 0.5932
Dataset id: 1778
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Tranche.sol, there is no slippage check to deposit, withdraw, mint and redeem.  
Users should pay balancing fee and balancing fee is calculated using balance of junior and senior tranches. As a result, when users deposit or withdraw, actual paid balancing fee can be different from expected.  
The function returns balancingFee or 0 according to the getDynamicReserveRatio  
```solidity
function getBalancingFee(address tranche, bool isDeposit, uint256 assets) external view override returns (uint256) {
    if ((getDynamicReserveRatio(tranche, isDeposit, assets) * 100) > balancingDeltaThreshold) {
        if ((tranche == address(junior) && isDeposit) || (tranche == address(senior) && !isDeposit)) {
            return balancingFee;
        }
    }
    if ((getDynamicReserveRatio(tranche, isDeposit, assets) * 100) < 1e4 - balancingDeltaThreshold) {
        if ((tranche == address(senior) && isDeposit) || (tranche == address(junior) && !isDeposit)) {
            return balancingFee;
        }
    }
    return 0;
}
```
The calculates the reserve ratio using current balances of tranches.  
```solidity
function getDynamicReserveRatio(address tranche, bool isDeposit, uint256 assets) public view returns(uint256){
    IERC20 asset = IERC20(junior.asset());
    if (asset.balanceOf(address(senior)) == 0 && asset.balanceOf(address(junior)) == 0) {
        return targetReserveRatio;
    }
    if(tranche == address(junior)){
        return isDeposit ? (100 * (asset.balanceOf(address(junior)) + assets)) / (asset.balanceOf(address(junior)) + asset.balanceOf(address(senior)) + assets) : (100 * (asset.balanceOf(address(junior)) - assets)) / (asset.balanceOf(address(junior)) + asset.balanceOf(address(senior)) - assets);
    }
    else{
        return isDeposit ? (100 * asset.balanceOf(address(junior))) / (asset.balanceOf(address(junior)) + asset.balanceOf(address(senior)) + assets) : (100 * asset.balanceOf(address(junior))) / (asset.balanceOf(address(junior)) + asset.balanceOf(address(senior)) - assets);
    }
}
```
Internal pre-conditions  
None  
External pre-conditions  
1. None  
Attack Path  
Let's consider the following scenario:  
• Alice tries to deposit and expected balancing fee is 0.  
• Another users change the balance of junior and senior tranches before Alice's transaction is executed.  
• Current balancing fee is changed to balancingFee and her transaction is executed.  
Alice should pay unexpected balancing fee and receive less shares than expected amount.  
Liquidity providers may receive fewer assets or shares than expected from the tranche when depositing or withdrawing.

## Recommendation
Add the slippage check to the deposit, withdraw, mint and redeem function in the tranche contract.
