# [M] NFT metadata may reveal before mint

## Summary
Severity: Medium
Reporter: ashirleyshe
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L97-L101
Type: audit-issue

## Details
# NFT metadata may reveal before mint

## Summary
NFT metadata may reveal before mint

## Vulnerability Detail

If all the files are already uploaded to IPFS, someone could snipe the rares once they know the baseURI since most follow the format baseURI/tokenID, so once tokenID 1 is revealed and the URI format is known, you could see any NFT metadata. 

```solidity
    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");

        string memory baseURI_ = _baseURI();
        return bytes(baseURI_).length > 0 ? string(abi.encodePacked(baseURI_, tokenId.toString(), ".json")) : "";
    }
```

## Impact

1. Attackers can find out where the rares are.
2. Attackers may create a fake nft website, and mint out the entire set — using the same images and metadata.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L97-L101

## Tool used

Manual Review

## Recommendation

Move away from a decentralized server to a private API to serve up the metadata. If the token ID is minted already, we know the request is legit, so we show the metadata.
But, once the entire series is minted out, we can pop that metadata back onto IPFS and let it live on in a decentralized way.
