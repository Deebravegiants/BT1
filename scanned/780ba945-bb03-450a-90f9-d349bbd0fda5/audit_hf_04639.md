# [M] M-03 | Malicious Bid Gas Griefing

## Summary
Severity: Medium
Contest weight: 0.1391
Dataset id: 22378
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DN404 contract has a public setSkipNFT function where the msg.sender can assign a true or false skip status to themselves. A malicious actor may abuse this functionality to place bids on listed NFTs which would gas grief the lister upon acceptance with the following steps:
• Call setSkipNFT to set their skip status to true.
• Accumulate many ERC20 DN404 tokens by minting through the token contract, but no NFTs since they have a skip status of true.
• Call setSkipNFT to set their skip status to false.
• Place bids on listed DN404 NFTs, such that if they are accepted the lister would have to expend a significant amount of gas to mint the NFTs corresponding to the accounts pre-existing ERC20 balance. This can result in an unexpected loss of funds for the lister through gas expenditure, or even allow for the creation of bids which cannot be accepted as their execution cost would exceed the block gas limit.

## Recommendation
Be aware of this risk and document it for users. Consider overriding and disabling the setSkipNFT function to remove this potential griefing vector.
