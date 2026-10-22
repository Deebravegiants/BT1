# [M] Improper withdraw() in TargetVaultDopple

## Summary
Severity: Medium
Contest weight: 0.4507
Dataset id: 12063
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Feeder protocol, it supports a number of target vaults and each vault essentially acts as the corresponding investment strategy. Each target vault inherits from the base contract TargetVault, which defines the standard APIs, including deposit(), withdraw(), emergencyWithdrawAll(), harvest(), and collectFees(). If we examine the withdraw() routine in the TargetVaultDopple contract, this routine allows for withdrawing from the target vault to the central feed vault (line 150). It needs to be clarified that the withdraw() expects the token amount argument, while the internal doppleStaking.withdraw() expects a share amount. The interface mismatch may result in an inappropriate amount of tokens being withdrawn.
```solidity
* @dev Withdraw from target vault to target vault
function withdraw(uint256 _amount) external virtual onlyVault {
    if (_amount > 0) {
        depositedBalance -= _amount;
        doppleStaking.withdraw(address(this), pid, _amount);
        uint256 _balance = dopLP.balanceOf(address(this));
        // Redeem dopLP back to Token
        uint256 _tokenBefore = token.balanceOf(address(this));
        if (_balance > 0) {
            dopLP.safeIncreaseAllowance(address(dopPool), _balance);
            dopPool.removeLiquidityOneToken(_balance, getDoppleTokenIndex(), 0, block.timestamp + 600);
            uint256 _tokenAfter = token.balanceOf(address(this));
            uint256 _tokenAmount = _tokenAfter.sub(_tokenBefore);
            // Send token back to FeedVault
            token.safeTransfer(feedVault, _tokenAmount);
        }
        if (depositedBalance == 0) {
            cachedPricePerShare = 1e18;
        } else {
            cachedPricePerShare = targetPricePerShare();
        }
        emit Withdrawed(_amount);
    }
}
```

## Recommendation
Be consistent in using the actual token amounts for withdrawal. The above withdraw() routine needs to properly transform the token amount into the corresponding share amount.
