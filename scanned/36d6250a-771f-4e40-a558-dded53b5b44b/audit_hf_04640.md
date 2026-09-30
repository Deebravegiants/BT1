# [M] M-04 | Purchase Price May Significantly Differ Based On The Currency

## Summary
Severity: Medium
Contest weight: 0.1241
Dataset id: 22379
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can buy Album NFTs with ETH or USDC based on their preference. These token prices are predetermined (0.004 ETH or 15 USDC) and immutable. However, since this is a long term project, there will definitely be significant price movements in terms of ETH/USDC. Users will always choose to buy with the lower price. None of the users will buy with ETH when the ETH price increases in the long term and the protocol will still get $15 per token in that scenario. However, in the other scenario when ETH price goes down, users will buy with ETH at a much cheaper price. Even if ETH goes to $2500, NFT price per token will be $10 and it is 33% discount in expected sale price.

## Recommendation
One option is giving the owner the right to arrange prices based on market movements. The other option is determining a minimum token price in terms of USD value, and charging users at least corresponding amount of ETH if it requires more than 0.004 ETH. Consider choosing an option based on the protocol’s intentions since the former increases the owner power and the latter requires an oracle implementation and increases complexity.
