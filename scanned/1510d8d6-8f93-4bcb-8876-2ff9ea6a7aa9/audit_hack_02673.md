# [H] `ERC1155.isApprovedForAll(owner, receiver)` logic means it is possible for an approved receiver to steal vault shares in next epochs.

## Summary
Severity: High
Reporter: joestakey
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L164-L165
Type: audit-issue

## Details
# `ERC1155.isApprovedForAll(owner, receiver)` logic means it is possible for an approved receiver to steal vault shares in next epochs.

## Summary
Because of the way approval works for ERC1155 tokens, it is possible for an approved receiver to steal vault shares.

## Vulnerability Detail
The `redeem(uint256 tokenId, address receiver,  address owner) external` function allows an approved `receiver` to redeem vault `shares` against claim tokens of an `owner`.


This is done with a check in using `ERC1155.isApprovedForAll(owner, receiver)`.

The problem is that there is no way to approve a `receiver` for a specific epoch: `isApprovedForAll(owner, receiver)` means the `receiver` can redeem all the tokens of the `owner`, regardless of the `id` - ie regardless of the epoch in question.

Example:
- Alice owns `1,000` claim tokens for the epoch `M`.
- Alice grants approval to Bob to redeem her shares for epoch `M`.
- Bob calls `redeem(M, Bob, Alice)`.
- Several days later, Alice deposits collateral in the vault during epoch `N`. She receives `1,000` tokens for the epoch `N`
- Upon the new epoch starting, tokens of epoch `N` are now redeemable. Bob calls `redeem(N, Bob, Alice)` and receives shares without Alice realizing.

Bob effectively stole Alice's Vault shares of epoch `N`.

## Impact
An approved receiver can steal a user's vault shares in future epochs.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L164-L165


## Tool used
Manual Review

## Recommendation
This is an inherent issue to ERC1155 tokens: approval cannot be granted to a specific `id`

A potential mitigation could be to override all `ERC1155` functions moving tokens (`_safeTransferFrom`, `_mint`, `_burn` and their batch versions), adding the following line:

```solidity
_operatorApprovals[account][operator] = false
```

ensuring an `owner` approves a `receiver` for one `_redeem` call only.
