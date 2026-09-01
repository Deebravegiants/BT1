# [M] In reward calculation, dust amount is left and stuck in the contract for every epoch

## Summary
Severity: Medium
Chain: Smart contract
Component: Fenix-
Published: 2024-07-13
Source: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/46
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xe5a9b42a2793537a95cd2b51884dd64816b2eb94a7ec90beea86d0a93611761d
**Severity:** medium

**Description:**
**Description**

When rewards calculation happens, rewards accures with reward per epoch and the token's proportion of the total supply to determine the reward amount. Thus, every time, the remainder which is less than `supply` are left in the contract 

**Proof of Concept (PoC) File**
```solidity
    function _calculateRewardPerEpoch(uint256 tokenId_, uint256 epoch_) internal view returns (uint256) {
        uint256 balance = VirtualRewarderCheckpoints.getAmount(
            tokensInfo[tokenId_].balanceCheckpoints,
            tokensInfo[tokenId_].checkpointLastIndex,
            epoch_
        );

        uint256 supply = VirtualRewarderCheckpoints.getAmount(totalSupplyCheckpoints, totalSupplyCheckpointLastIndex, epoch_);

        if (supply == 0) {
            return 0;
        }

        return (balance * rewardsPerEpoch[epoch_ + _WEEK]) / supply;
//@audit-issue dust rewards are lost in every epoch
    }

```

**Revised Code File (Optional)**

The left amount of rewards should be added to next epoch or current epoch for distribution. This will motivate to current stakers to harvest rewards timely 

```solidity
    function _calculateRewardPerEpoch(uint256 tokenId_, uint256 epoch_) internal view returns (uint256) {
        uint256 balance = VirtualRewarderCheckpoints.getAmount(
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/46_
