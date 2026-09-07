# [M] _claimRewardsOnBehalf() User's rewards may be lost

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-03
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/10
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/e3d2681503499e81915797c77eeef8210352a138/contracts/plugins/assets/aave/StaticATokenLM.sol#L459-L461


# Vulnerability details

## Impact
Incorrect determination of maximum rewards, which may lead to loss of user rewards

## Proof of Concept
`_claimRewardsOnBehalf()` For users to retrieve rewards

```solidity
    function _claimRewardsOnBehalf(
        address onBehalfOf,
        address receiver,
        bool forceUpdate
    ) internal {
        if (forceUpdate) {
            _collectAndUpdateRewards();
        }

        uint256 balance = balanceOf(onBehalfOf);
        uint256 reward = _getClaimableRewards(onBehalfOf, balance, false);
        uint256 totBal = REWARD_TOKEN.balanceOf(address(this));

@>      if (reward > totBal) {
@>          reward = totBal;
@>      }
        if (reward > 0) {
@>          _unclaimedRewards[onBehalfOf] = 0;
            _updateUserSnapshotRewardsPerToken(onBehalfOf);
            REWARD_TOKEN.safeTransfer(receiver, reward);
        }
    }
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/10_
