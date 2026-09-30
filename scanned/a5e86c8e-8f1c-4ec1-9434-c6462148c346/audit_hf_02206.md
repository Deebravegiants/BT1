# [H] Revisited Logic of CoverPool::_startNextEpoch()

## Summary
Severity: High
Contest weight: 0.6359
Dataset id: 12220
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Hegic Herge protocol, the CoverPool contract implements an incentive mechanism that rewards
the staking of the supported coverToken token with the profitToken token. In particular, the internal
_startNextEpoch() routine called inside the privilege fixProfit() routine is used to settle the last
reward epoch and start a new reward epoch.
While examining its logic, we observe its current
implementation should be improved.
To elaborate, we show below the related code snippet of the CoverPool contract. By design,
the epoch[currentEpoch].cumulativePoint records the accumulated rewards per share at the begin-
ning of the currentEpoch epoch and the cumulativeProfit records the latest accumulated rewards
per share (i.e., the accumulated rewards per share at the end of the currentEpoch epoch).
Inside the _startNextEpoch() routine, the statement of uint256 profitOut = totalShare == 0 ? 0 : ((
cumulativeProfit - epoch[currentEpoch].cumulativePoint)* coverTokenTotal())/ ADDITIONAL_DECIMALS
(line 307) is designed to calculate the total rewards shared by the total withdrawal in the currentEpoch
epoch.
Apparently, the current implementation does not meet the requirement.
Given this, we
suggest to improve the implementation as below: uint256 profitOut = totalShareOut == 0 ? 0 : ((
cumulativeProfit - epoch[currentEpoch].cumulativePoint)* totalShareOut)/ ADDITIONAL_DECIMALS (line
307).
Moreover, inside the _startNextEpoch() routine, it comes to our attention that the totalShare is
updated (line 314) but the corresponding coverToken balance (i.e., coverTokenTotal()) is not, which
will make the pool share expensive and require necessary revision.
```solidity
function fixProfit() external onlyRole(DEFAULT_ADMIN_ROLE) {
    uint256 profitAmount = profitToken.balanceOf(address(this)) - profitTokenBalance;
    profitTokenBalance += profitAmount;
    cumulativeProfit += (profitAmount * ADDITIONAL_DECIMALS) / totalShare;
    _startNextEpoch();
    emit Profit(currentEpoch, profitAmount);
}

function _startNextEpoch() internal {
    require(
        MINIMAL_EPOCH_DURATION <= block.timestamp - epoch[currentEpoch].start,
        "The epoch is too short to be closed"
    );
    uint256 totalShareOut = epoch[currentEpoch].totalShareOut;
    uint256 coverTokenOut = totalShare == 0 ? 0 : (totalShareOut * coverTokenTotal()) / totalShare;
    uint256 profitOut = totalShare == 0 ? 0 : ((cumulativeProfit - epoch[currentEpoch].cumulativePoint) * coverTokenTotal()) / ADDITIONAL_DECIMALS;
    epoch[currentEpoch].coverTokenOut = coverTokenOut;
    epoch[currentEpoch].profitTokenOut = profitOut;
    totalShare -= epoch[currentEpoch].totalShareOut;
}
```

## Recommendation
Correct the implementation of the _startNextEpoch() routine as above-mentioned.
