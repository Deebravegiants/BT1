# [M] Reward tokens will be locked and not distributed because of rounding error

## Summary
Severity: Medium
Chain: Smart contract
Component: Fenix-
Published: 2024-07-17
Source: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/58
Type: hats-finding

## Details
**Github username:** @rilwan99
**Twitter username:** Ril11111
**Submission hash (on-chain):** 0x88464bfff74b60ada18845e79f46f9512801e1bd03fbbf64641565959d636c94
**Severity:** medium

**Description:**
**Description**\
The reward calculation for users in the `SingelTokenVirtualRewarderUpgradeable.sol` is based on the user's token proportion of the total supply across unclaimed epochs. The function is defined below:

    function calculateRewardPerEpoch(uint256 tokenId, uint256 epoch) internal view returns (uint256) {
        // Balance of the user at the last checkpoint nearest to the epoch
        uint256 balance = VirtualRewarderCheckpoints.getAmount( 
            tokensInfo[tokenId].balanceCheckpoints,
            tokensInfo[tokenId].checkpointLastIndex,
            epoch
        );
        // Total balance in the contract at the last checkpoint nearest to the epoch
        uint256 supply = VirtualRewarderCheckpoints.getAmount(totalSupplyCheckpoints, totalSupplyCheckpointLastIndex, epoch);
        if (supply == 0) {
            return 0;
        }
        // @Audit: Precision loss
        return (balance * rewardsPerEpoch[epoch + WEEK]) / supply;
    }

This function suffers from precision loss due to integer division

**Attack Scenario**\
If:
- `supply > (balance * rewardsPerEpoch[epoch + WEEK])`


In such cases, the calculation results in 0, effectively denying rewards to users with smaller balances relative to the total supply. This scenario becomes increasingly likely as the pool of users attaching their NFTs to the strategy grows.
- Rounding Down: 

Due to integer division, all results are rounded down. This means that even when users should receive a fractional reward, they receive only the integer part, losing the fractional portion.

**Impact**\

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/58_
