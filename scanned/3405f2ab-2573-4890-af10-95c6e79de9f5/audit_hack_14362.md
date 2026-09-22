# [H] [HIGH] MeritDutchAuction#setNFT - Missing ERC721 check could lead to an unusable contract

## Summary
Severity: High
Reporter: vangrim
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91
Type: audit-issue

## Details
# [HIGH] MeritDutchAuction#setNFT - Missing ERC721 check could lead to an unusable contract

## Summary
The setNFT function of the `MeritDutchAuction` contract does not include a verification process to ensure the input contract abides by the ERC721 standards. A non-ERC721 compatible contract can render the auction contract unusable.

## Vulnerability Detail
The **`setNFT`** function within the **`MeritDutchAuction`** contract is designed to set the address of the NFT contract. However, there's an absence of a verification mechanism to validate if the provided contract address adheres to the ERC721 standard. This omission might lead to an improper contract address being set. As a result, it can affect the minting functionality because the **`mint`** function relies on the ERC721 standard's **`mint`** function.

In the contract, the **`setNFT`** function is particularly important because it is only callable by the owner, and only once. If a non-ERC721 compatible contract is set initially, it would not be possible to correct this mistake, potentially rendering the **`MeritDutchAuction`** contract ineffective.

## Impact
This vulnerability may cause the mint function to fail, disrupting the ability to generate NFTs. This is a severe issue since the `MeritDutchAuction` contract revolves around the minting and auctioning of NFTs, which would be severely hampered if the NFT contract isn't ERC721 compliant.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91

```solidity
function setNFT(address nft_) external onlyOwner {
    // Can only be set once
    require(address(nft) == address(0), "NFT already set");
    // NFT contract must allow this contract to mint NFTs
    nft = MeritNFT(nft_);
}
```

## Tool used

Manual Review

## Recommendation
It is highly recommended to incorporate a verification check to ensure ERC721 compliance. You can use the **`supportsInterface`** function from the ERC165 standard to check if the provided contract supports the ERC721 interface.

Add a `require` check as per below:
```solidity
function setNFT(address nft_) external onlyOwner {
        // Can only be set once
        require(address(nft) == address(0), "NFT already set");
        // NFT contract must allow this contract to mint NFTs
        require(MeritNFT(nft_).supportsInterface(0x80ac58cd), "Not ERC721 compliant");
	nft = nft_;
    }
```
