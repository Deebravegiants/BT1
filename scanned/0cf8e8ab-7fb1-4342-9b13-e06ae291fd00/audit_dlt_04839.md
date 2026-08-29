# [M] Presale minting may not be able to mint the amount that they should be

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/120
Type: sherlock-finding

## Details
Chom

medium

# Presale minting may not be able to mint the amount that they should be

## Summary
Presale minting may not be able to mint the amount that they should be

## Vulnerability Detail
https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L176-L190

If the user may mint only 1 NFT on presale, _presaleMinted[msg.sender] will be true causing the user to lose the opportunity to mint the remaining tokens.

## Impact
If UX is not good, the user may mint only 1 NFT on presale. Once minted, they can't mint more. Losing the opportunity to mint the remaining tokens.

## Code Snippet
https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L176-L190

## Tool used

Manual Review

## Recommendation

Track minted amount instead of true false flag

```solidity
 function presaleMint(uint256 amount, bytes32[] calldata proof) 
     external 
     payable 
     paymentProvided(amount * _runtimeConfig.presaleMintPrice) 
 { 
     require(presaleActive(), "Presale has not started yet"); 
     require( 
         isWhitelisted(msg.sender, proof), 
         "Not whitelisted for presale" 
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/120_
