# [H] function transferERC721 does not delete timelockERC721s if the token was among locked tokens

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-visorfinance
Published: 2021-05-17
Source: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/13
Type: code-finding

## Details
# Handle

paulius.eth


# Vulnerability details

## Impact
function timeUnlockERC721 deletes timelockERC721s after removing NFT, so I expect a similar behavior with function transferERC721. It iterates over timelockERC721Keys and if it finds the token among locked tokens, it does some extra checks and later removes this token but does not delete timelockERC721s.

## Recommended Mitigation Steps
Solution: delete timelockERC721s possibly in the for loop if you find the right token.
