# [M] Possible Assets Locked in SmartChef

## Summary
Severity: Medium
Contest weight: 0.5933
Dataset id: 12502
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MetaFinanceTriggerPool contract provides an interface (i.e. projectPartyEmergencyWithdraw()) for project administrator to withdraw user assets from the SmartChef pool at emergency. Our analysis shows its current implementation needs to be improved. To elaborate, we show below the code snippets from the MetaFinanceTriggerPool contract. The projectPartyEmergencyWithdraw() routine is used to withdraw user assets from the given smartChef_ and update the protocol lock with the given urgent_. After the withdraw, it reduces the totalPledgeValue which is the total pledge that is deposited in all supported smartChef pools.
```solidity
function projectPartyEmergencyWithdraw(
    ISmartChefInitializable smartChef_,
    bool urgent_
) external nonReentrant onlyRole(PROJECT_ADMINISTRATOR) {
    if (totalPledgeAmount != 0) {
        smartChef_.emergencyWithdraw();
        totalPledgeValue = totalPledgeValue.sub(storageQuantity[smartChef_]);
        storageQuantity[smartChef_] = 0;
    }
    if (urgent_) {
        urgent = urgent_;
    }
}
```
It comes to our attention that, the totalPledgeValue may be reduced to be smaller than the proportion value. Based on this, the updateMiningPool() will not trigger withdraw from all smartChef pools. And if the totalPledgeValue value becomes larger than the proportion value again in the reinvest() routine, it will overwrite the storageQuantity[i] which records the amount of deposit in each smartChef pool. As a result of this, the original deposit amounts are lost, and the deposited assets have no way to be withdrawn anymore.
```solidity
/**
 * @dev Update mining pool
 * @notice Batch withdraw, and will experience token swap to cake token, and increase the rewards for all users
 */
function updateMiningPool() private nonReentrant {
    cakeTokenBalanceOf = cakeTokenAddress.balanceOf(address(this));
    if (totalPledgeValue > proportion && smartChefArray.length > 0) {
        uint256 length = smartChefArray.length;
        address[] memory path = new address[](3);
        path[1] = address(wbnbTokenAddress);
        path[2] = address(cakeTokenAddress);
        for (uint256 i = 0; i < length; ++i) {
            uint256 rewardTokenBalanceOf = IERC20Metadata(smartChefArray[i].rewardToken()).balanceOf(address(this));
            if (storageQuantity[smartChefArray[i]] != 0) {
                smartChefArray[i].withdraw(storageQuantity[smartChefArray[i]]);
            }
            path[0] = smartChefArray[i].rewardToken();
            swapTokensForCake(IERC20Metadata(path[0]), path, rewardTokenBalanceOf);
        }
        uint256 haveAward = ((cakeTokenAddress.balanceOf(address(this))).sub(totalPledgeValue)).sub(cakeTokenBalanceOf);
        if (totalPledgeAmount != 0) {
            (uint256 userRewards, uint256 exchequerRewards) = totalUserRewards(haveAward);
            exchequerAmount = exchequerAmount.add(exchequerRewards);
            takenTransfer(address(this), address(this), userRewards);
        } else {
            exchequerAmount = exchequerAmount.add(haveAward);
        }
    }
}
/**
 * @dev Bulk pledge
 */
function reinvest() private nonReentrant {
    totalPledgeValue = (cakeTokenAddress.balanceOf(address(this))).sub(cakeTokenBalanceOf);
    if (totalPledgeValue > proportion && smartChefArray.length > 0) {
        uint256 _frontProportionAmount = 0;
        uint256 _arrayUpperLimit = smartChefArray.length;
        for (uint256 i = 0; i < _arrayUpperLimit; ++i) {
            if (i != _arrayUpperLimit - 1) {
                storageQuantity[smartChefArray[i]] = (totalPledgeValue.mul(storageProportion[smartChefArray[i]]))
                    .div(proportion);
                _frontProportionAmount += storageQuantity[smartChefArray[i]];
            }
            if (i == _arrayUpperLimit - 1) {
                storageQuantity[smartChefArray[i]] = totalPledgeValue.sub(_frontProportionAmount);
            }
        }
        for (uint256 i = 0; i < _arrayUpperLimit; ++i) {
            cakeTokenAddress.safeApprove(address(smartChefArray[i]), 0);
            cakeTokenAddress.safeApprove(address(smartChefArray[i]), storageQuantity[smartChefArray[i]]);
            smartChefArray[i].deposit(storageQuantity[smartChefArray[i]]);
        }
    }
}
```
What's more, the same issue exists in the setProportion() routine where the proportion is updated which could also impact the deposit/withdraw with the smartChef pools.

## Recommendation
Revisit the above mentioned routines to properly maintain the deposit amounts in all smartChef pools.
