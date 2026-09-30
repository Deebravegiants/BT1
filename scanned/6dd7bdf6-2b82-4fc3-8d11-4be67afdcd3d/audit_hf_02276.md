# [M] Revisited Logic To Calculate The Rewards

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 12456
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The WombatStaking contract interacts with the Wombat Exchange to provide services, such as adding new liquidity, staking LP token on MasterWombat, and staking WOM to get veWom. It provides an external harvest() interface for users or WombatPoolHelper to claim rewards from MasterWombat. To elaborate, we show below the code snippet of the harvest() routine. By design, it is implemented to claim rewards from the specified pool in MasterWombat and send the rewards to the rewarder. Specially, if the caller is not the Magpie contracts, the caller can get the caller fee in mWom. The original fee in WOM is locked to get veWom via the convertWOM() routine (line 347). After that, the routine transfers mWom to the caller (line 348). However, currently the contract may not hold mWom at all, which reverts the harvest operation. Our analysis shows that the WOM rewards will be converted to the mWom by invoking uint fee = IMWom(mWom).convert(feeAmount) and the received mWom amount (fee) may not be equal to the feeAmount as the veWom may not be converted from WOM with the 1:1 conversion rate. As a result, it needs to transfer the fee amount of mWom to the caller: IERC20(mWom).safeTransfer(msg.sender, fee).

```solidity
/// @notice harvest a Pool from MGP
/// @param _depositToken the address of the deposit token Pool to harvest
/// @param _isUser true if this function is not called by the magpie Contracts. The caller gets the caller fee
function harvest(
    address _depositToken,
    bool _isUser
) _onlyActivePool(_depositToken) external {
    Pool storage poolInfo = pools[_depositToken];
    uint256 beforeBalance = IERC20(wom).balanceOf(address(this));
    uint256[] memory pids = new uint256[](1);
    pids[0] = poolInfo.pid;
    IMasterWombat(masterWombat).multiClaim(pids); // only claim from a specific deposit token Pool
    uint256 rewards = IERC20(wom).balanceOf(address(this)) - beforeBalance;
    uint256 afterFee = rewards;
    if (_isUser) {
        uint256 feeAmount = (rewards * CALLER_FEE) / FEE_DENOMINATOR;
        IERC20(wom).approve(mWom, feeAmount);
        this.convertWOM(feeAmount);
        IERC20(mWom).safeTransfer(msg.sender, feeAmount);
        afterFee = afterFee - feeAmount;
    }
    sendRewards(poolInfo.depositToken, poolInfo.rewarder, rewards, afterFee);
    emit WomHarvested(rewards, rewards - afterFee);
}

/// @notice convert WOM to mWOM
/// @param _amount the number of WOM to convert
/// @dev the WOM must already be in the contract
function convertWOM(uint256 _amount) external returns(uint256) {
    uint256 veWomMintedAmount = 0;
    if (_amount > 0) {
        IERC20(wom).approve(veWom, _amount);
        veWomMintedAmount = IVeWom(veWom).mint(_amount, IVeWom(veWom).maxLockDays());
        emit WomConverted(_amount, IVeWom(veWom).maxLockDays());
    }
    return veWomMintedAmount;
}
```

## Recommendation
Revisit the above logic to properly convert the WOM to mWom and transfer the received amount of mWom to the caller.
