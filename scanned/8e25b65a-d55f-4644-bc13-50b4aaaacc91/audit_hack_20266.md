# [M] **3.3.5** getAllHeldIds() **of** LSSVMPairMissingEnumerable **is vulnerable to a

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
denial of service attack**

**Severity:** Medium Risk

**Context:** LSSVMPairMissingEnumerable.sol#L90-97,LSSVMPair.sol#L

**Description:** The contractLSSVMPairMissingEnumerable tries to compensate
for NFT contracts that do not haveERC721Enumerableimplemented. However,
this cannot be done for everything as it is possible to usetransferFrom()to
send an NFT from the same collection to thePair. In that case the callbackon-
ERC721Received()will not be triggered and theidSetadministration ofLSSVM-
PairMissingEnumerablewill not be updated. This means thatnft().balanceO
f(address(this));can be different from the elements inidSet. Assuming an
actor accidentally, or on purpose, usestransferFrom()to send additional NFTs
to thePair,getAllHeldIds()will fail asidSet.at(i)for unregistered NFTs will
fail. This can be used in a griefing attack.

getAllHeldIds()inLSSVMPairMissingEnumerable:

```
function getAllHeldIds() external view override returns (uint256[] memory) {
uint256 numNFTs = nft().balanceOf(address(this)); // returns the registered
,! + unregistered NFTs
uint256[] memory ids = new uint256[](numNFTs);
for (uint256 i; i < numNFTs; i++) {
ids[i] = idSet.at(i); // will fail at the unregistered NFTs
}
return ids;
}
```
The following checks performed with_nft.balanceOf()might not be accurate
in combination with LSSVMPairMissingEnumerable. Risk is low because any
additional NFTs making later calls to_sendAnyNFTsToRecipient()and_send-
SpecificNFTsToRecipient()will fail. However, this might make it more difficult
to troubleshoot issues.


```
function swapTokenForAnyNFTs(...) .. {
...
require((numNFTs > 0) && (numNFTs <= _nft.balanceOf(address(this))),"Ask
,! for > 0 and <= balanceOf NFTs");
...
_sendAnyNFTsToRecipient(_nft, nftRecipient, numNFTs); // could fail
...
}
function swapTokenForSpecificNFTs(...) ... {
...
require((nftIds.length > 0) && (nftIds.length <=
_nft.balanceOf(address(this))),"Must ask for > 0 and < balanceOf NFTs"); //
'<' should be '<='
```
```
,!
,!
...
_sendSpecificNFTsToRecipient(_nft, nftRecipient, nftIds);// could fail
...
}
```
**Note:** The error string< balanceOf NFTsis not accurate.

**Recommendation:** Spearbit recommends Sudoswap to useidSet.length()
in order to determine the number of NFTs by changing the code in accordance
with the followingdiff:

- uint256 numNFTs = nft().balanceOf(address(this));
+ uint256 numNFTs = idSet.length();

To accessidSet.length()fromLSSVMPair, an extra function is necessary in
LSSVMPairMissingEnumerable.solandLSSVMPairEnumerable.sol.

Spearbit also suggests to fix the error string inswapTokenForSpecificNFTs.

**Sudoswap:** Addressed in this branch here. idSetsize is now used instead of
NFT balanceOf.

**Spearbit:** Acknowledged.
