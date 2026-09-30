# [M] Adjusted Authentication of setLockedAt()

## Summary
Severity: Medium
Contest weight: 0.4012
Dataset id: 11692
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Augmented Finance protocol has a built-in incentive mechanism to reward protocol users upon a variety of protocol operations, such as mint(), redeem(), borrow(), and repay(). It also designs the necessary incentive mechanism for the team. In the following, we examine the TeamRewardPool contract. To elaborate, we show below the setUnlockedAt() routine. It comes to our attention that it currently allows the team manager to adjust the reward lockup timestamp. This is inappropriate as only the controller should be able to adjust the reward lockup timestamp.
```solidity
function setUnlockedAt(uint32 at) external onlyTeamManagerOrController {
    require(at > 0, "unlockAt required");
    console.log("setUnlockedAt", _lockupTill, getCurrentTick(), at);
    require(_lockupTill == 0 || _lockupTill >= getCurrentTick(), "lockup is finished");
    _lockupTill = at;
}
```

## Recommendation
Revise the onlyTeamManagerOrController modifier of the above setUnlockedAt() routine to be onlyController.
