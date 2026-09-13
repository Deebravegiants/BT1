# [M] The contracts miss certain functions that brick the operability

## Summary
Severity: Medium
Reporter: sorrynotsorry
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L10
Type: audit-issue

## Details
# The contracts miss certain functions that brick the operability

## Summary
The contracts miss certain functions that brick the operability
## Vulnerability Detail
`MeritNFT` contract inherits OZ's `AccessControlEnumerable` contract.

`AccessControlEnumerable` implements `_grantRole` & `_revokeRole` functions which are internal and should be called internally inside a function in MeritNFT contract. But these functions don't exist. While these two functions serve for enumeration, the deployer can call `AccessControl`'s `grantRole` & `revokeRole`. However, it's not the enumerated version and the mapping kept in AccessControl is different for the role distributions.


## Impact
Break of composability
## Code Snippet

```solidity
contract MeritNFT is ERC721Enumerable, AccessControlEnumerable {
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L10)
## Tool used

Manual Review

## Recommendation
Implement functions to internally call AccessControlEnumerable's internal functions.
