# [M] Proper pendingRewards() Calculation in BinoDistributionLaw

## Summary
Severity: Medium
Contest weight: 0.4570
Dataset id: 11730
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Binopoly has built-in incentive mechanisms to engage protocol users. While reviewing a specific BinoFarm pool, we notice the BinoDistributionLaw approach to compute pendingRewards() may return incorrect rewards. To elaborate, we show below this function. Notice that the protocol is designed to reset the user's inject point to 0 for the new round and the new round is determined when the user's _lastTimeInject[account][lid] is at least CONTEST_DURATION + CLAIM_DURATION earlier. However, the following implementation shows it is determined as block.timestamp > _lastTimeInject[account][lid].add(CONTEST_DURATION) (line 146), which needs to be revised as block.timestamp > _lastTimeInject[account][lid].add(CONTEST_DURATION).add(CLAIM_DURATION).

```solidity
// in Bino decimal, 1e18
function pendingRewards(address account, uint256 lid) public view returns (uint256) {
    require(lid > 0 && lid <= 7, "land id is out of range of [1, 7]");
    if (!isClaimTime) {
        return 0;
    }
    if (block.timestamp > _lastTimeInject[account][lid].add(CONTEST_DURATION)) {
        uint256 thisRank = 0;
        for (uint256 i = 0; i < rankForThisRound.length; ++i) {
            if (lid == rankForThisRound[i]) {
                thisRank = i.add(1); // from 1 to 3
                break;
            }
        }
        if (thisRank == 0) {
            return 0;
        }
        uint256 rankShare;
        if (thisRank == 1) {
            rankShare = _totalRewardBalance.mul(152).div(TOTAL_ALLO_POINTS); // 1e18
        } else if (thisRank == 2) {
            rankShare = _totalRewardBalance.mul(69).div(TOTAL_ALLO_POINTS); // 1e18
        } else {
            rankShare = _totalRewardBalance.mul(25).div(TOTAL_ALLO_POINTS); // 1e18
        }
        return _injectedPointsOf[account][lid].mul(rankShare).div(_totalInjectedPointsOf[lid]);
    }
    return 0;
}
```

The claimBinoRewards() function in the same contract shares the same issue.

## Recommendation
Revise the above-mentioned functions to properly determine whether the new round is entered.
