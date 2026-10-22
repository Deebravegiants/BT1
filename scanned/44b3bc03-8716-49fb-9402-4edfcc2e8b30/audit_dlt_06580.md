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
These issues become increasingly problematic as the pool of users attaching their NFTs to the strategy grows, exacerbating the precision problem for users with smaller stakes and leading to a cumulative loss of rewards for all users due to rounding down.

**Attachments**

1. **Proof of Concept (PoC) File**

Initial State
- Total Supply: 1,000,000 tokens
- Rewards per Epoch: 900 tokens
- User A Balance: 1000 tokens (0.1% of supply)
- Rest of the pool: 1,000,000 tokens (99.9% of supply)
Reward Calculation for One Epoch:
- For User A: (1000 * 900) / 1,000,000 = 0 (due to integer division)

**Exploitation and Cumulative Effect**

User A receives no rewards despite being entitled to 0.1% of the tokens for the above epoch. If `rewardsPerEpoch` for the rest of the unharvested epoch remains the same/ decreases, user A would have effectively not receive ANY reward for participating in this strategy. 


2. **Recommendation**

Introduce a scaling factor to the calculations. This approach allows more decimal places to be maintained during the calculation and then scale back down at the end.
```
function calculateRewardPerEpoch(uint256 tokenId, uint256 epoch) internal view returns (uint256, uint256) {
    uint256 balance = VirtualRewarderCheckpoints.getAmount(
        tokensInfo[tokenId].balanceCheckpoints,
        tokensInfo[tokenId].checkpointLastIndex,
        epoch
    );
    uint256 supply = VirtualRewarderCheckpoints.getAmount(totalSupplyCheckpoints, totalSupplyCheckpointLastIndex, epoch);
    if (supply == 0) {
        return (0, 0);
    }

    // Introduce a scaling factor, e.g., 1e18 for 18 decimal places of precision
    uint256 PRECISION_FACTOR = 1e18;

    // Scale up the calculation
    uint256 scaledReward = (balance * rewardsPerEpoch[epoch_ + _WEEK] * PRECISION_FACTOR) / supply;

    // Round to the nearest whole number
    uint256 roundedReward = (scaledReward + PRECISION_FACTOR / 2) / PRECISION_FACTOR;

    return roundedReward;
}
```

2. **Mitigation**

This approach solves the vulnerability by:

1. Preventing small balances from resulting in zero rewards due to integer division.
2. Maintaining precision throughout the calculation, which is especially important when dealing with large supply values.
3. Providing fair rounding to the nearest whole number, ensuring that users receive rewards when they're due more than half a token.
