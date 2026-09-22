# [M] Convex `BaseRewardPool` allows Claim on Behalf which causes delta to break - Loss of all Rewards

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1425
Type: code-finding

## Details
# Lines of code

https://etherscan.io/address/0x9D5C5E364D81DaB193b72db9E9BE9D8ee669B652#code#L979
https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L254-L277


# Vulnerability details

### Impact
The Convex `BaseRewardPool` has a function `getReward(address _account, bool _claimExtras)`, which allows claiming on behalf of other accounts:

https://etherscan.io/address/0x9D5C5E364D81DaB193b72db9E9BE9D8ee669B652#code#L979

```solidity
    function getReward(address _account, bool _claimExtras) public updateReward(_account) returns(bool){
        uint256 reward = earned(_account);
        if (reward > 0) {
            rewards[_account] = 0;
            rewardToken.safeTransfer(_account, reward);
            IDeposit(operator).rewardClaimed(pid, _account, reward);
            emit RewardPaid(_account, reward);
        }

        //also get rewards from linked rewards
        if(_claimExtras){
            for(uint i=0; i < extraRewards.length; i++){
                IRewards(extraRewards[i]).getReward(_account);
            }
        }
        return true;
    }
```

The [`ConvexTryCriptoStrategy`](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L254-L277) uses delta balances to determine the amount of tokens gained

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L254-L277

```solidity
        uint256[] memory balancesBefore = new uint256[](tempData.tokens.length); /// @audit Delta B4
        for (uint256 i = 0; i < tempData.tokens.length; i++) {
            balancesBefore[i] = IERC20(tempData.tokens[i]).balanceOf(
                address(this)
            );
        }

        zap.claimRewards(
            tempData.rewardContracts,
            tempData.extraRewardContracts,
            tempData.tokenRewardContracts,
            tempData.tokenRewardTokens,
            extrasTempData.depositCrvMaxAmount,
            extrasTempData.minAmountOut,
            extrasTempData.depositCvxMaxAmount,
            extrasTempData.spendCvxAmount,
            extrasTempData.options
        );
        uint256[] memory balancesAfter = new uint256[](tempData.tokens.length); /// @audit Delta After
        for (uint256 i = 0; i < tempData.tokens.length; i++) {
            balancesAfter[i] = IERC20(tempData.tokens[i]).balanceOf(
                address(this)
            );
        }
```

These delta balances can be made to return a zero or lower value by claiming on behalf of the strategy

By doing that, rewards will be lost

### POC
- ConvexTriCryptoStrategy has some gain
- Attack calls `getReward(STRATEGY, true)`
- The strategy shares value is reduced, the tokens are stuck in the strategy

### Mitigation

- Hardcode tokens the strategy will sell (e.g. Curve, CVX)
- Add a sweep to processor / owner to sell anything else that is not protected
- Use absolute values for tokens that are not the LP token nor WETH


## Assessed type

ERC4626
