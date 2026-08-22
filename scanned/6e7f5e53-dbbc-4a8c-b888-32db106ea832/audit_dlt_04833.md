# [M] NFT minting both public and presale doesn't have ending time check

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/128
Type: sherlock-finding

## Details
Chom

medium

# NFT minting both public and presale doesn't have ending time check

## Summary
NFT minting both public and presale doesn't have an ending time check

## Vulnerability Detail
https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L197-L202

https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L205-L210

mintingActive and presaleActive only check for a mint start but don't check for mint end

## Impact
Can't schedule the minting end time. Typical NFT minting always have a start and end time. And once the public sale is active, presale should end.

## Code Snippet
https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L197-L202

https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L205-L210

## Tool used

Manual Review

## Recommendation
Add end-time check and use >= for start time since it should start on the block that it written to be start

```solidity
 function mintingActive() public view returns (bool) { 
     // We need to rely on block.timestamp since it's 
     // easier to configure across different chains 
     // solhint-disable-next-line not-rely-on-time 
     return block.timestamp >= _runtimeConfig.publicMintStart && block.timestamp < _runtimeConfig.publicMintEnd; 
 } 
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/128_
