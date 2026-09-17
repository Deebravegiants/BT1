# [M] Ineffective Whitelist

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-aave-lens
Published: 2022-02-14
Source: https://github.com/code-423n4/2022-02-aave-lens-findings/issues/30
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-aave-lens/blob/aaf6c116345f3647e11a35010f28e3b90e7b4862/contracts/core/LensHub.sol#L146


# Vulnerability details

Creating profiles through `LensHub.createProfile` requires the caller to be whitelisted.

```solidity
function _validateCallerIsWhitelistedProfileCreator() internal view {
    if (!_profileCreatorWhitelisted[msg.sender]) revert Errors.ProfileCreatorNotWhitelisted();
}
```

However, a single whitelisted account can create as many profiles as they want and send the profile NFT to other users.
They can create unlimited profiles on behalf of other users which makes the whitelist not effective.

## Recommended Mitigation Steps
Consider limiting the number of profile creations per whitelisted user or severely limiting who is allowed to create profiles, basically making profile creation a centralized system.
