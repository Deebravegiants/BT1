# [M] Ineffective Whitelist

## Summary
Severity: Medium
Contest weight: 0.4122
Dataset id: 1535
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LensHub.sol#L146](https://github.com/code-423n4/2022-02-aave-lens/blob/aaf6c116345f3647e11a35010f28e3b90e7b4862/contracts/core/LensHub.sol#L146)  

Creating profiles through `LensHub.createProfile` requires the caller to be whitelisted.

```solidity
function _validateCallerIsWhitelistedProfileCreator() internal view {
    if (!_profileCreatorWhitelisted[msg.sender]) revert Errors.ProfileCreatorNotWhitelisted();
}
```

However, a single whitelisted account can create as many profiles as they want and send the profile NFT to other users.  
They can create unlimited profiles on behalf of other users which makes the whitelist not effective.

## Recommendation
Consider limiting the number of profile creations per whitelisted user or severely limiting who is allowed to create profiles, basically making profile creation a centralized system.

Declined, this is by design.

Governance will decide what contracts are allowed to mint via the allowlist. If governance wishes to have a more centralized system, it will only approve contracts that have numerical caps within their code.

I agree with the sponsor, I think this can already be handled by the governance strictly approving contracts with numerical caps or limiting the allowlist of who can create a profile. As such, I’m inclined to mark this as `invalid` because the recommendation can already be implemented or adhered to by the governance.

In light of another issue, I will mark this as a valid issue because [#66](https://github.com/code-423n4/2022-02-aave-lens-findings/issues/66) outlines a similar concern. The two issues reference different parts of the codebase so I think its fair to keep them distinct. However, I’d normally like to see a bit more detail on how non-whitelisted users can benefit from an infinite minter.
