# [M] TreasureDAO incident: The Arbitrum-based TreasureDAO NFT trading market was exposed and discovered a vulnerability. According to SlowMist analysis, the

## Summary
Severity: Medium
Target: TreasureDAO
Loss: -
Attack method: Unchecked Input Data
Published: 2022-03-03
Source: https://www.coindesk.com/tech/2022/03/03/stolen-smol-brains-nfts-returned-to-users-hours-after-treasure-exploit/
Type: slowmist-incident

## Details
The Arbitrum-based TreasureDAO NFT trading market was exposed and discovered a vulnerability. According to SlowMist analysis, the core of this vulnerability lies in the lack of judgment that the incoming _quantity parameter is not 0 before the ERC-721 standard NFT transfer, resulting in ERC -721 Standard NFT can be transferred directly and the cost of purchasing NFT is calculated as 0 when calculating the price. Hours after it was stolen, developers confirmed that hackers had begun returning stolen “Smol Brains” and other NFTs.
