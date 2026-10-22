# [M] ERC420._safeBatchTransferFrom() doesn't verify allowList Groge_Report.md

## Summary
Severity: Medium
Contest weight: 0.6956
Dataset id: 8582
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERC420 contract is designed to work with one type of NFT with id=0, so if a user has 100 full tokens then he has a 100 NFT of id=0 (as having one full token -1e18- will mint you one NFT, and having less than one full token -1e17 for example- will not mint you an NFT). When the user transfers his tokens, an equivalent amount of NFTs will be burnt from his balance if he is not in the allowList, and the receiver will be minted an equivalent amount of these transferred tokens if he is not in the allowList:
```solidity
uint256 balanceBeforeSender = _balances[from];
uint256 balanceBeforeReceiver = _balances[to];
if (!isInAllowlist(from)) {
    uint256 tokens_to_burn = (balanceBeforeSender / 10 ** _decimals) - ((balanceBeforeSender - value) / 10 ** _decimals);
    _nft_burn(from, 0, tokens_to_burn);
}
if (!isInAllowlist(to)) {
    uint256 tokens_to_mint = ((balanceBeforeReceiver + value) / 10 ** _decimals) - (balanceBeforeReceiver / 10 ** _decimals);
    _nft_mint(to, 0, tokens_to_mint);
}
_update(from, to, value);
```
so if userA transferred 3 tokens (3e18) to userB, then 3 NFTs will be burnt from userA if he is not in the allowList, and userB will be minted 3 NFTs if he is not in the allowList. safeBatchTransferFrom function is supposed to transfer a batch of NFTs with different ids from the sender to the receiver, but since the contract is designed to handle only one NFT type of id=0, then this function is considered as a dummy function that has no difference from the transfer function, where it will only handle transferring tokens of id=0:
Groge_Report.md
```solidity
function _safeBatchTransferFrom(
    uint256[] memory ids,
    uint256[] memory values
) internal {
    uint value;
    for (uint256 i = 0; i < ids.length; i++) {
        value += values[i];
    }
    _update(from, to, value * 10 ** _decimals);
    _nft_mint(to, 0, value);
```
But as can be noticed, the _safeBatchTransferFrom function burns the NFTs from the sender and mints the receiver without checking if they are in the allowList or not (similar check made in the transfer, safeTransferFrom & transferFrom functions). This will result in an inconsistency in the transfer mechanism across ERC420 transfer functions, where users in the allowList can be minted NFTs/ burning from their NFTs when transferring tokens via safeBatchTransferFrom() function.
Code Snippet
ERC420._safeBatchTransferFrom function
```solidity
function _safeBatchTransferFrom(
    uint256[] memory ids,
    uint256[] memory values
) internal {
    uint value;
    for (uint256 i = 0; i < ids.length; i++) {
        value += values[i];
    }
    _update(from, to, value * 10 ** _decimals);
    _nft_mint(to, 0, value);
```

## Recommendation
Since ERC420 contract is designed to handle only one NFT type (with id=0), update _safeBatchTransferFrom function to check if the sender/receiver are not in the allowList before burning/minting NFTs:
```solidity
function _safeBatchTransferFrom(
    uint256[] memory ids,
    uint256[] memory values
) internal {
    uint value;
    for (uint256 i = 0; i < ids.length; i++) {
        value += values[i];
    }
    _update(from, to, value * 10 ** _decimals);
-   _nft_mint(to, 0, value);
+   if (!isInAllowlist(from)) {
+   if (!isInAllowlist(to)) {
+       _nft_mint(to, 0, value);
+   }
+   }
```
