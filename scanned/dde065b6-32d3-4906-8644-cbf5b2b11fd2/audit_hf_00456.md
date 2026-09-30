# [H] In setReward(), block.timestamp

## Summary
Severity: High
Contest weight: 0.8359
Dataset id: 1885
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In setReward(), block.timestamp is used instead of startTime at lastUpdateTime. This results in reward distribution for the time, reward was not allocated for. In setReward(), owner can set rewards for present as well as future. Issue arises when owner sets rewards for future because at rewardData[rewardToken].lastUpdateTime, block.timestamp is used instead of startTime.
Internal pre-conditions
None
External pre-conditions
None
Attack Path
For easier calculation, duration is taken in hours
1. Suppose its 1PM, Alice staked 5e18 tokens.
2. And owner wanted to distribute a rewardToken(amount = 100e18) starting at 2PM till 6PM ie duration = 4 hours. Therefore, rewardRate = 100e18 / 4 hours = 25e18 tokens/hour & lastUpdateTime = 1PM
3. Now, there should not be any reward from 1PM to 2PM because reward started from 2PM.
4. However, Alice will receive reward for 1PM to 2PM also
Users will receive reward for the time, reward was not allocated for. In above case, for 1PM to 2PM

## Proof of Concept
```solidity
function test_rewardWillDistributeForWrongTime() public {
    //Alice deposited 5e18 tokens at 1PM
    address alice = makeAddr("Alice");
    vm.startPrank(alice);
    uint256 amount = 5e18;
    stakedToken.mint(alice, amount);
    stakedToken.approve(address(stakingContract), amount);
    stakingContract.stake(amount, alice);
    vm.stopPrank();
    //Owner set reward at 1PM but starting from 2PM
    vm.startPrank(owner);
    MockedMintableERC20 rewardToken = new MockedMintableERC20("Rewards", "Rewards");
    uint256 startTime = block.timestamp + 1 hours;
    uint256 endTime = startTime + 4 hours;
    uint256 totalRewards = 100e18;
    rewardToken.mint(owner, totalRewards);
    rewardToken.approve(address(stakingContract), totalRewards);
    stakingContract.setReward(address(rewardToken), startTime, endTime, totalRewards);
    vm.stopPrank();
    //Alice is claiming after 1 hour ie 2PM
    vm.warp(block.timestamp + 1 hours + 1);
    vm.roll(block.number + 1);
    vm.startPrank(alice);
    stakingContract.claim();
    //balanceOf alice should be 0 but it is ~25e18 & stakingContract is ~ 75e18
    console.log("balanceOf alice: ", rewardToken.balanceOf(alice));
    console.log("balanceOf stakingContract: ", rewardToken.balanceOf(address(stakingContract)));
    vm.stopPrank();
}
```
Result:
Ran 1 test for tests/lending-pool/StakingRewards.t.sol:StakingRewardsTest
[PASS] test_rewardWillDistributeForWrongTime() (gas: 992944)
Logs:
balanceOf alice: 25006944444444442840
balanceOf stakingContract: 74993055555555557160

## Recommendation
```solidity
function setReward(address rewardToken, uint256 startTime, uint256 endTime, uint256 totalRewards)
    public
    onlyOwner
    nonReentrant
    updateReward(address(0))
{
    ...
    startTime = Math.max(block.timestamp, startTime);
    rewardData[rewardToken].startTime = startTime;
    rewardData[rewardToken].endTime = endTime;
    // rewardData[rewardToken].lastUpdateTime = block.timestamp;
    rewardData[rewardToken].lastUpdateTime = startTime;
    ...
}
```
