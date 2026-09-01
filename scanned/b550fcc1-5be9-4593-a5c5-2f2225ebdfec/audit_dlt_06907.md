# [M] Undesired behavior

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-nested
Published: 2022-02-10
Source: https://github.com/code-423n4/2022-02-nested-findings/issues/6
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-nested/blob/69cf51d8e4eeb8bce3025db7f4f74cc565c9fad3/contracts/NestedRecords.sol#:~:text=uint256%20amount%20%3D%20records,_nftId%5D.reserve%20%3D%20_reserve%3B


# Vulnerability details

You push a parameter into an array of tokens without checking if it's already exists. And if at first it's added with amount 0 it can later on be pushed with a greater amount and be twice in the array. Then in all processing it will consider the first occurrence and therefore the occurrence with amount 0.

         NestedRecords.store pushed the parameter _token
