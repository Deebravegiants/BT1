# [H] EIP-721 / EIP-1155 Re-Entrancy Vulnerability

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-07
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/8
Type: code-finding

## Details
# Handle

0xsomeone


# Vulnerability details

## Impact

The impact of this finding is difficult to estimate as the contract system within scope is limited in how the various components are meant to be utilized. 

A definitive side-effect of this re-entrancy is the delayed application of the `afterRedeemHook` which, in some implementations, renders NFTs illegible which would not be the case during the re-entrancy's execution. Another side-effect is that the `quantity1155` or `holdings` would be out-of-sync and would indicate the NFT / EIP-1155 token amount to still be "in the system" when it is not.

## Proof of Concept

The `safeTransferFrom` implementations of both `ERC1155` and `ERC721` in `withdrawNFTsTo` contain a callback hook on the recipient of the transfer in case they are a contract as the standard dictates that smart contract recipients should be aware of the transfer.

While re-entrancies are prevented via the `nonReentrant` modifier for most system functions, they are not done so for `swapTo` (and consequently `swap`) invocations meaning that it is still possible to re-enter the system at this stage. Additionally, re-entrancy is still possible in other segments of the codebase i.e. ones that rely on the eligibility contracts.

## Tools Used

Manual Review.

## Recommended Mitigation Steps

The `afterRedeemHook` paradigm should be changed to a `beforeRedeemHook` paradigm to ensure that all state changes are applied prior to external calls according to the Checks-Effects-Interactions pattern. Additionally, the state changes within `withdrawNFTsTo` should occur prior to the `safeTransferFrom` invocations.
