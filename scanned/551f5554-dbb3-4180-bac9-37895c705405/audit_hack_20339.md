# [M] 5.2.10balanceOf()can be circumvented via reentrancy and two pairs

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** LSSVMPairERC1155.sol#L222-L

**Description:** A reentrancy issue can occur if two pairs with the same ERC1155 NFTid are deployed. Via a call to
swap NFTs, the ERC1155 callbackonERC1155BatchReceived()is called. This callback can start a second NFT
swap via a second pair. As the second pair has its own reentrancy modifier, this is allowed.

This way thebalanceOf()check of_takeNFTsFromSender()can be circumvented. If a reentrant call, to a second
pair, supplies a sufficient amount of NFTs then thebalanceOf()check of the original call can be satisfied at the
same time.

We haven't found a realistic scenario to abuse this with the current routers.

Permissionless routers will certainly increase the risk as they can abuseisRouter == true. If the router is mali-
cious then it also has other ways to steal the NFTs; however with the reentrancy scenario it might be less obvious
this is happening.

Note: ERC777 tokens also contain such a callback and have the same interface as ERC20 so they could be used
in an ERC20 pair.

```
function _takeNFTsFromSender(IERC1155 _nft, uint256 numNFTs, bool isRouter, address routerCaller) ... {
```
```
if (isRouter) {
```
```
uint256 beforeBalance = _nft.balanceOf(_assetRecipient, _nftId);
```
```
router.pairTransferERC1155From(...);// reentrancy with other pair
require((_nft.balanceOf(_assetRecipient, _nftId) - beforeBalance) == numNFTs, ...);//
,! circumvented
} else {
```
```
}
}
```
**Recommendation:**

1. Thoroughly verify routers before whitelisting them.
2. To protect against reentrancy issues involving multiple pairs, consider putting the reentrancy storage variable
    on a common location, for example in theLSSVMPairFactory.

**Sudorandom Labs:** Solved in PR#83 and PR#93.

**Spearbit:** Verified that this is fixed by PR#83 and PR#93.
