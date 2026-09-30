# [M] Improved Overﬂow/Underﬂow Prevention in vote()

## Summary
Severity: Medium
Contest weight: 0.4608
Dataset id: 12836
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Quoll V2 protocol implements the bribe feature, which enables Quoll users to vote on how to distribute the voting powers among all the supported MasterWombat pools.
The user can get the voting power by locking QUO in the VlQuoV2 contract. While reviewing the implementation of the voting functionality, we notice the contract is built on solidity 0.6.12 and there is potential overflow/underflow risk for the arithmetic operations.
In the following, we take the BribeManager::vote() routine as an example and show the potential overflow/underflow risk. At the beginning of the routine, it adds all the delta votes into the totalUserVote (line 245). The addition is not guarded against possible overflow. In particular, if some of the delta votes are oversized, the addition of delta to totalUserVote may overflow to yield a much smaller negative integer. Similarly, the subtraction of the totalUserVote from the totalVlQuoInVote (line 281) is not guarded against possible underflow. If the totalUserVote is undersized, the subtraction may underflow to yield a much bigger integer.
Note the same issue is also applicable to the unvote()/SmartConverter::_depositFor() routines, etc.
```solidity
function vote(
    address[] calldata _lps,
    int256[] calldata _deltas
) external override {
    uint256 length = _lps.length;
    int256 totalUserVote;
    for (uint256 i; i < length; i++) {
        Pool memory pool = poolInfos[_lps[i]];
        require(pool.isActive, "Not active");
        int256 delta = _deltas[i];
        totalUserVote += delta;
        if (delta != 0) {
            if (delta > 0) {
                poolTotalVote[pool.lpToken] += uint256(delta);
                userTotalVote[msg.sender] += uint256(delta);
                userVoteForPools[msg.sender][pool.lpToken] += uint256(delta);
                IVirtualBalanceRewardPool(pool.rewarder).stakeFor(msg.sender, uint256(delta));
            } else {
                poolTotalVote[pool.lpToken] -= uint256(-delta);
                userTotalVote[msg.sender] -= uint256(-delta);
                userVoteForPools[msg.sender][pool.lpToken] -= uint256(-delta);
                IVirtualBalanceRewardPool(pool.rewarder).withdrawFor(msg.sender, uint256(-delta));
            }
        }
        emit VoteUpdated(msg.sender, pool.lpToken, userVoteForPools[msg.sender][pool.lpToken]);
    }
    if (msg.sender != delegatePool) {
        // this already gets updated when a user vote for the delegate pool
        if (totalUserVote > 0) {
            totalVlQuoInVote += uint256(totalUserVote);
        } else {
            totalVlQuoInVote -= uint256(-totalUserVote);
        }
    }
    require(userTotalVote[msg.sender] <= getUserLocked(msg.sender), "Above vote limit");
}
```

## Recommendation
Use a higher solidity version (>0.8.0) which integrates auto safeMath check or add proper overflow/underflow prevention like the safeMath.
