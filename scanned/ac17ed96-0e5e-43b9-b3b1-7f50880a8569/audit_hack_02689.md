# [M] Use safeMint when mint ERC1155 (QueueInternal.sol)

## Summary
Severity: Medium
Reporter: Trumpero
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L95
Type: audit-issue

## Details
# Use safeMint when mint ERC1155 (QueueInternal.sol)

## Lines of code 
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L95

## Vulnerability Detail
The `_mint()` method is used instead of `_safeMint()`, presumably to save gas. I however argue that this isn’t recommended because:
* [OpenZeppelin’s documentation](https://docs.openzeppelin.com/contracts/4.x/api/token/erc721#ERC721-_mint-address-uint256-) discourages the use of transferFrom(), use safeTransferFrom() whenever possible
* If `msg.sender` is a contract and is not aware of incoming ERC1155 tokens, the sent tokens could be locked forever

## Impact
sent tokens ERC1155 could be locked 

## Tool used
Manual Review

## Recommendation
use `_safeMint` instead
