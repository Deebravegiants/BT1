# [M] Using ERC20.decimals() that ERC20's optional method

## Summary
Severity: Medium
Reporter: exd0tpy
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L57-L58
Type: audit-issue

## Details
# Using ERC20.decimals() that ERC20's optional method

## Summary
Using ERC20.decimals() that ERC20's optional method.

## Vulnerability Detail
According to [EIP-20](https://eips.ethereum.org/EIPS/eip-20) method `decimals` are optional. They comment like this `This method can be used to improve usability, but interfaces and other contracts MUST NOT expect these values to be present`.

Some ERC20 token are may not implement decimals, so if that token are used by KNOX it will revert.

## Impact
Initialize of Auction will revert when supporting ERC20 token that doesn't implement decimals.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L57-L58

## Tool used
Manual Review

## Recommendation
Using try catch when call decimals() and handle it.
