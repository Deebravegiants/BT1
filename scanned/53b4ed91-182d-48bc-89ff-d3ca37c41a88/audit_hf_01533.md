# [M] Multiple centralization attack vectors are present in the protocol

## Summary
Severity: Medium
Contest weight: 0.1321
Dataset id: 8180
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol owner has privileges to control the funds in the protocol or the flow of them.
The mint function in FlorinToken is callable by the contract owner, which is FlorinTreasury, but FlorinTreasury has the transferFlorinTokenOwnership method. This makes it possible that the FlorinTreasury deployer to mint as many FlorinToken tokens to himself as he wants, on demand.
The withdraw method in FlorinStaking works so that the owner can move all of the staked florinToken tokens to any wallet, including his.
The setMDCperFLRperSecond method in FlorinStaking works so that the owner can stop the rewards at any time or unintentionally distribute them in an instant.
The method setFundingTokenChainLinkFeed allows the owner to set any address as the new Chainlink feed, so he can use an address that he controls and returns different prices based on rules he decided.

## Recommendation
Consider removing some owner privileges or put them behind a Timelock contract or governance.
Discussion
pashov: Acknowledged.
