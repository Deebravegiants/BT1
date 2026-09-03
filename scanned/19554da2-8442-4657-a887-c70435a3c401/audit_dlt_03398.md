# [H] Missing allValidNFTs and afterRedeemHook with swapTo?

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-09
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/20
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
The function swapTo of NFTXVaultUpgradeable.sol is kind of a combination of mintTo and redeemTo (the code looks very similar to a combination of mintTo and redeemTo).
Before receiveNFTs I would expect a call to allValidNFTs, like in mintTo.
This is to make sure only eligible NFTs are transferred. Without this check any NFT could be transferred.

After withdrawNFTsTo I would expect a call to afterRedeemHook, like in redeemTo.
The afterRedeemHook fixes the administration for the eligability. Without this the eligibility administrations would be flawed.

This way swapTo would circumvent the checks of mintTo and redeemTo and would allow any NFT to be transferred (even the one's that are not eligible)

## Proof of Concept
NFTXVaultUpgradeable.sol

function mintTo(..)
  ...
        require(allValidNFTs(tokenIds), "NFTXVault: not eligible");
        uint256 count = receiveNFTs(tokenIds, amounts);

 function redeemTo(uint256 amount, uint256[] memory specificIds, address to)
   ....
        uint256[] memory redeemedIds = withdrawNFTsTo(amount, specificIds, to);
        afterRedeemHook(redeemedIds);

 function swapTo(..)
        ...
        uint256 count = receiveNFTs(tokenIds, amounts);
        ...
        uint256[] memory ids = withdrawNFTsTo(count, specificIds, to);
      

## Tools Used

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-05-nftx-findings/issues/20_
