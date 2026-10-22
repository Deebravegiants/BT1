# [M] LPS-2 | onERC721Received Reentrancy

## Summary
Severity: Medium
Contest weight: 0.0908
Dataset id: 9330
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the unstakeAndWithdrawLpToken function, the msg.sender may re-enter into the onERC721Received function upon the withdrawToken call by transferring the withdrawn Uniswap V3 LP NFT back to the LPStaker. This reentrancy can yield an unexpected state where the token still exists in the tokensStaked list for the owner, but not in the idToOwner or stakedIndex. Such an unexpected state may have unintended consequences and effect frontend systems reading from the contract or third party systems built on top of the LPStaker.

## Recommendation
Move the withdrawToken call to the end of the for loop to follow Check-Effects-Interactions. Alternatively, add a reentrancy check to the onERC721Received function.
