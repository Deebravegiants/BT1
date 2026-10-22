# [H] Morpho rewards can not be claimed due to missing claimRewardsForToken implementation

## Summary
Severity: High
Contest weight: 0.5817
Dataset id: 5492
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MorphoVaultRouter is an extension of the ERC4626Router designed speciﬁcally for Morpho Vaults. Morpho vault depositors not only earn interest from underlying borrowers but also accrue MORPHO token rewards, as Morpho incentivizes lending. However, since the router contract is the entity supplying funds to Morpho, it accrues all MORPHO rewards on behalf of its depositors. To claim these rewards, the admin of the MorphoVaultRouter must call claimRewardsForToken:
```solidity
function claimRewardsForToken(IERC20 token, uint amount, bytes32[] calldata proof, address receiver)
external
onlyAdmin
{
    MORPHO_REWARD_DISTRIBUTOR.claim(msg.sender, address(token), amount, proof);
    token.transfer(receiver, amount);
    emit RewardsClaimed(token, amount, receiver);
}
```
When a router is deployed for a speciﬁc Kandel, the router’s admin is transferred to ERC4626Kandel. After the rewards are collected, the Kandel must call adminWithdrawTokens to withdraw them. The issue is that ERC4626Kandel has no way to call claimRewardsForToken on the router, which results in lost Morpho rewards.

## Recommendation
Consider creating an ERC4626Kandel tailored for Morpho that can call claimRewardsForToken.
