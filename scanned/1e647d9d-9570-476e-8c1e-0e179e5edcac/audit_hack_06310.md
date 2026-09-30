# [M] Early Compiler Version Used

## Summary
Severity: Medium
Reporter: 0xAgro
Source: https://github.com/ethereum/solidity-blog/blob/499ab8abc19391be7b7b34f88953a067029a5b45/_posts/2022-06-15-inline-assembly-memory-side-effects-bug.md
Type: audit-issue

## Details
# Early Compiler Version Used

## Summary

Solidity 0.8.18 is used in `MintableERC721.sol` which, as of the start of the contest, is [only 2 weeks old](https://blog.soliditylang.org/2023/02/01/solidity-0.8.18-release-announcement/).

## Vulnerability Detail

By using a compiler version early you are volunteering as guinea pigs for potential bugs when it is not necessary. As an example in [Solidity 0.8.13](https://blog.soliditylang.org/2022/03/16/solidity-0.8.13-release-announcement/), [a compiler bug](https://github.com/ethereum/solidity-blog/blob/499ab8abc19391be7b7b34f88953a067029a5b45/_posts/2022-06-15-inline-assembly-memory-side-effects-bug.md) was found 81 days after the release announcement (see links).

## Impact

User funds or the general function of Fair Funding could be at risk if a high severity bug were to be found in Solidity 0.8.18.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/solidity/MintableERC721.sol#L2

## Tool used

Manual Review

## Recommendation

Use an older and more battle-tested version of Solidity.
