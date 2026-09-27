# [H] Chainswap incident: The cross-chain bridge Chainswap announced the details of the stolen incident on its official blog. A total of 20 project assets w

## Summary
Severity: High
Target: Chainswap
Loss: $ 4,000,000
Attack method: Contract Vulnerability
Published: 2021-07-11
Source: https://chain-swap.medium.com/chainswap-exploit-11-july-2021-post-mortem-6e4e346e5a32
Type: slowmist-incident

## Details
The cross-chain bridge Chainswap announced the details of the stolen incident on its official blog. A total of 20 project assets were stolen, with a total value of approximately US$4 million. At present, the ChainSwap team has reached a consensus with the affected projects and initially formulated and implemented a compensation plan. According to the project investigation, due to the error in the token cross-chain quota code, the on-chain swap bridge quota is automatically increased by the signature node, the purpose of which is to be more decentralized without manual control. However, due to a logical flaw in the code, this led to a vulnerability that automatically increases the number of invalid addresses that are not whitelisted.
