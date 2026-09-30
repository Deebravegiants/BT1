# [M] getAllHeldIds() of LSSVMPairMissingEnumerable is vulnerable to a denial of service attack

## Summary
Severity: Medium
Contest weight: 0.5971
Dataset id: 15656
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract LSSVMPairMissingEnumerable tries to compensate for NFT contracts that do not have ERC721Enumerable implemented. However, this cannot be done for everything as it is possible to use transferFrom() to send an NFT from the same collection to the Pair. In that case the callback onERC721Received() will not be triggered and the idSet administration of LSSVMPairMissingEnumerable will not be updated. This means that nft().balanceOf(address(this)); can be different from the elements in idSet. Assuming an actor accidentally, or on purpose, uses transferFrom() to send additional NFTs to the Pair, getAllHeldIds() will fail as idSet.at(i) for unregistered NFTs will fail. This can be used in a grieving attack.

```solidity
function getAllHeldIds() external view override returns (uint256[] memory) {
    uint256 numNFTs = nft().balanceOf(address(this)); // returns the registered + unregistered NFTs
    uint256[] memory ids = new uint256[](numNFTs);
    for (uint256 i; i < numNFTs; i++) {
        ids[i] = idSet.at(i); // will fail at the unregistered NFTs
    }
    return ids;
}
```

The following checks performed with _nft.balanceOf() might not be accurate in combination with LSSVMPairMissingEnumerable. Risk is low because any additional NFTs making later calls to _sendAnyNFTsToRecipient() and _sendSpecificNFTsToRecipient() will fail. However, this might make it more difficult to troubleshoot issues.

```solidity
function swapTokenForAnyNFTs(...) .. {
    ...
    require((numNFTs > 0) && (numNFTs <= _nft.balanceOf(address(this))), "Ask for > 0 and <= balanceOf NFTs");
    ...
    _sendAnyNFTsToRecipient(_nft, nftRecipient, numNFTs); // could fail
    ...
}
```

```solidity
function swapTokenForSpecificNFTs(...) ... {
    ...
    require((nftIds.length > 0) && (nftIds.length <= _nft.balanceOf(address(this))), "Must ask for > 0 and <= balanceOf NFTs"); // '<' should be '<='
    ...
    _sendSpecificNFTsToRecipient(_nft, nftRecipient, nftIds); // could fail
    ...
}
```

## Recommendation
Spearbit recommends Sudoswap to use idSet.length() in order to determine the number of NFTs by changing the code in accordance with the following diff:

```
- uint256 numNFTs = nft().balanceOf(address(this));
+ uint256 numNFTs = idSet.length();
```

To access idSet.length() from LSSVMPair, an extra function is necessary in LSSVMPairMissingEnumerable.sol and LSSVMPairEnumerable.sol.
