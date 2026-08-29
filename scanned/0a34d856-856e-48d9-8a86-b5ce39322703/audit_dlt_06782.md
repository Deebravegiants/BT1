# [H] missing isEpochClaimed validation

## Summary
Severity: High
Chain: Smart contract
Component: 2023-05-ajna
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-ajna-findings/issues/132
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-ajna/blob/276942bc2f97488d07b887c8edceaaab7a5c3964/ajna-core/src/RewardsManager.sol#L135-L198


# Vulnerability details

## Impact
User can claim rewards even when is already claimed

## Proof of Concept

The _claimRewards function is using to calculate and send the reward to the caller but this function is no validating if isEpochClaimed mapping is true due that in claimRewards function is validated, see the stament in the following lines:

```
file: ajna-core/src/RewardsManager.sol
function claimRewards(
        uint256 tokenId_,
        uint256 epochToClaim_ 
    ) external override {
        StakeInfo storage stakeInfo = stakes[tokenId_];

        if (msg.sender != stakeInfo.owner) revert NotOwnerOfDeposit(); 

        if (isEpochClaimed[tokenId_][epochToClaim_]) revert AlreadyClaimed(); // checking if the epoch was claimed;

        _claimRewards(
            stakeInfo,
            tokenId_,
            epochToClaim_,
            true,
            stakeInfo.ajnaPool
        );
    }
```
https://github.com/code-423n4/2023-05-ajna/blob/276942bc2f97488d07b887c8edceaaab7a5c3964/ajna-core/src/RewardsManager.sol#L114-L125

Now the moveStakedLiquidity is calling _claimRewards too without validate isEpochClaimed mapping:

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-ajna-findings/issues/132_
