# [M] Incorrect Fee-Handling Logic in FeeHelper

## Summary
Severity: Medium
Contest weight: 0.4466
Dataset id: 12540
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the fee collection and distribution, the Mu protocol provides a FeeHelper contract. The collected fee may be distributed to a number of entities, including vault, keeper, treasury, and pool. Our analysis on the fee-distribution logic indicates it needs to be improved.
In the following, we show the implementation of the aﬀected dealFee() routine. The fee distribution to the four above-mentioned entities follows the intended design. However, the distribution to treasury is checked on the condition of if(keeper != address(0)&& projectFeeP > 0) (line 101), which should be revised as if(treasury != address(0)&& projectFeeP > 0).
```solidity
function dealFee(address trader, address keeper, uint256 totalFee, uint256 position) internal {
    require(standardToken.balanceOf(address(this)) >= totalFee, "amount mismatching");
    totalFee = dealRefereReward(totalFee, trader, position);
    if (vault != address(0) && vaultFeeP > 0) {
        uint amount = totalFee * vaultFeeP / MILLAGE_DENOMINATOR;
        SafeERC20.safeTransfer(standardToken, vault, amount);
        IVault(vault).distributeReward(amount, false);
    }
    if (keeper != address(0) && orderKeeperFee > 0) {
        uint amount = totalFee * orderKeeperFee / MILLAGE_DENOMINATOR;
        SafeERC20.safeTransfer(standardToken, keeper, amount);
    }
    if (keeper != address(0) && projectFeeP > 0) {
        uint amount = totalFee * projectFeeP / MILLAGE_DENOMINATOR;
        SafeERC20.safeTransfer(standardToken, treasury, amount);
    }
    if (pool != address(0) && lpFeeP > 0) {
        uint amount = totalFee * lpFeeP / MILLAGE_DENOMINATOR;
        standardToken.approve(pool, amount);
        IRewardPool(pool).increaseAccTokens(amount);
    }
}
```

## Recommendation
Revise the above dealFee() routine to properly distribute collected fees.
