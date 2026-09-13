# [M] OpenZeppelin `AccessControl._setupRole()` is deprecated, use `_grantRole()` instead

## Summary
Severity: Medium
Reporter: ret2basic.eth
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/e50c24f5839db17f46991478384bfda14acfb830/contracts/access/AccessControl.sol#L204C6-L204C67
Type: audit-issue

## Details
# OpenZeppelin `AccessControl._setupRole()` is deprecated, use `_grantRole()` instead

## Summary

OpenZeppelin `AccessControl._setupRole()` is deprecated. Use `_grantRole()` instead.

## Vulnerability Detail

In OpenZeppelin `AccessControl.sol`, it says `_setupRole()` is deprecated in its Natspec:

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/e50c24f5839db17f46991478384bfda14acfb830/contracts/access/AccessControl.sol#L204C6-L204C67

```plaintext
* NOTE: This function is deprecated in favor of {_grantRole}.
```

This function could be removed in further versions of `AccessControl.sol`. Using deprecated function can make `MeritNFT.sol` undeployable.

## Impact

`MeritNFT.sol` can be undeployable in the future.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L53-L54

## Tool used

Manual Review

## Recommendation

Use `_grantRole()` instead of `_setupRole()`.
