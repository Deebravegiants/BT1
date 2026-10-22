# [M] tfFarm stake earns a reward token but the reward token isn't immediately sent to LIQUIDITY_MINING_RECEIVER

## Summary
Severity: Medium
Reporter: Chom
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L102-L104
Type: audit-issue

## Details
# tfFarm stake earns a reward token but the reward token isn't immediately sent to LIQUIDITY_MINING_RECEIVER

## Summary
tfFarm stake earns a reward token but the reward token isn't immediately sent to LIQUIDITY_MINING_RECEIVER

## Vulnerability Detail
Once _deposit is called, it will convert USDC -> tfUSDC and stake tfUSDC in the farm. If you are staking second time, it will also send a reward token to the strategy contract. It should forward the reward token sent to the LIQUIDITY_MINING_RECEIVER, but currently, it is struck in the strategy contract until claimReward is called.

```solidity
        if (stakerRewards[token].claimableReward[msg.sender] > 0) {
            _claim(token);
        }
```

## Impact
LIQUIDITY_MINING_RECEIVER won't receive TrueFi reward tokens until they call claimReward. But the TrueFi reward tokens have already been sent to the contract on staking.

## Code Snippet
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L102-L104

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueMultiFarm.sol#L133-L142

## Tool used

Manual Review

## Recommendation
Transfer reward to LIQUIDITY_MINING_RECEIVER after staking

```solidity
  function _deposit() internal override whenNotPaused {
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L469
    tfUSDC.join(want.balanceOf(address(this)));

    // Don't stake in the tfFarm if shares are 0
    // This would make the function call revert
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueMultiFarm.sol#L101
    if (tfFarm.getShare(tfUSDC) == 0) return;

    // How much tfUSDC is in this contract
    // Could both be tfUSDC that was already in here before the `_deposit()` call
    // And new tfUSDC that was minted in the `tfUSDC.join()` call
    uint256 tfUsdcBalance = tfUSDC.balanceOf(address(this));

    // Stake all tfUSDC in the tfFarm
    tfFarm.stake(tfUSDC, tfUsdcBalance);
    
    // How much TrueFi tokens does this contract hold
    uint256 rewardBalance = rewardToken.balanceOf(address(this));

    // Send all TrueFi tokens to LIQUIDITY_MINING_RECEIVER
    if (rewardBalance != 0) rewardToken.safeTransfer(LIQUIDITY_MINING_RECEIVER, rewardBalance);
  }
```
