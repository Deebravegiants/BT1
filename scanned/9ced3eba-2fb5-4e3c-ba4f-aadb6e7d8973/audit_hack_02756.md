# [M] claimReward function in TrueFiStrategy.sol failed to claim reward if we have no reward to claim.

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L189
Type: audit-issue

## Details
# claimReward function in TrueFiStrategy.sol failed to claim reward if we have no reward to claim.

## Summary

claimReward function in TrueFiStrategy.sol failed to claim reward if we have no reward to claim, and we waste gas and user may wonder why there is no reward to claim. 

We can check if we have reward to claim before claiming and preview the claimable reward.

## Vulnerability Detail

the implementation of the claimReward function in TrueFiStrategy is 

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L189

```solidity
  function claimReward() external {
    IERC20[] memory tokens = new IERC20[](1);
    tokens[0] = tfUSDC;

    // Claim TrueFi tokens for tfUSDC
    tfFarm.claim(tokens);

    // How much TrueFi tokens does this contract hold
    uint256 rewardBalance = rewardToken.balanceOf(address(this));

    // Send all TrueFi tokens to LIQUIDITY_MINING_RECEIVER
    if (rewardBalance != 0) rewardToken.safeTransfer(LIQUIDITY_MINING_RECEIVER, rewardBalance);
  }
```

we directly call 

```solidity
tfFarm.claim(tokens);
```

but it is possible that we have no reward to claim. 

## Impact

we waste gas and user may wonder why there is no reward to claim after we can claim function.

## Code Snippet

## Tool used

Manual Review

## Recommendation

There is a function inside the tfFram

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueMultiFarm.sol#L251

```solidity
    /**
     * @dev View to estimate the claimable reward for an account that is staking token
     * @return claimable rewards for account
     */
    function claimable(IERC20 token, address account) external view returns (uint256) {
```

we can call this function to check if we are eligible to claim reward.

```solidity
  function claimReward() external {
    IERC20[] memory tokens = new IERC20[](1);
    tokens[0] = tfUSDC;

    // Claim TrueFi tokens for tfUSDC
    uint256 claimableReward = tfFarm.claimable(tfUSDC, address(this));
    if(claimableReward > 0) {
        tfFarm.claim(tokens);
    }

    // How much TrueFi tokens does this contract hold
    uint256 rewardBalance = rewardToken.balanceOf(address(this));

    // Send all TrueFi tokens to LIQUIDITY_MINING_RECEIVER
    if (rewardBalance != 0) rewardToken.safeTransfer(LIQUIDITY_MINING_RECEIVER, rewardBalance);
  }
```

we can also add a function to let user preview the claimable reward

```solidity
   function claimableReward() external view returns external view returns (uint256) {
      return tfFarm.claimable(tfUSDC, address(this));
   }
```
