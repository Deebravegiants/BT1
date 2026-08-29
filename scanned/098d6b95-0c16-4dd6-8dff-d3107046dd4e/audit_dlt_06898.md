# [H] Unbounded loops

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-visorfinance
Published: 2021-05-17
Source: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/9
Type: code-finding

## Details
# Handle

paulius.eth


# Vulnerability details

## Impact
Unbounded for loops may exceed gas limit. There are several places where iterations over dynamically sized arrays take place. For example, function _removeNft iterates over all the NFTs and tries to find the one that is needed to be removed. However, iterating over a dynamically sized array is dangerous because if there are too many items stored it may exceed block gas limit before reaching the right element. It may not be impossible to remove the NFT if the nfts array becomes too large. Same issue is possible with getBalanceLocked that iterates over the unbounded list of _lockSet. If this list grows too large, it may become impossible to execute functions that use it (transferERC20, delegatedTransferERC20, timeUnlockERC20).

## Recommended Mitigation Steps
Refactor to use mappings instead of arrays (or store indexes separately) or introduce size limits on arrays that will prevent such cases.
