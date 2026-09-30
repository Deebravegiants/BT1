# [M] Withdrawing after a slash event before the

## Summary
Severity: Medium
Contest weight: 0.2270
Dataset id: 1721
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In LidoVault::withdraw(), when the vault has started but not ended, it limits the value to withdraw if a slashing event occured and withdraws that withdraw will get more than their initial deposit in case the Lido ratio comes back up (likely during the vault's duration).
It's clear from the code users should get exactly their initial amount of funds or since the vault has started only withdraw their initial deposit equivalent stETH at the start of the vault- unless we are in a loss amount than it should.
Internal pre-conditions
None.
External pre-conditions
Lido slash, which is in scope as per the readme.
The Lido Liquid Staking protocol can experience slashing incidents (such as this https://blog.lido.fi/post-mortem-launchnodes-slashing-incident/).
These incidents will decrease income from deposits to the Lido Liquid Staking protocol and could decrease the stETH balance. The contract must be operational after it
Attack Path
1. Lido slashes, decreasing the steth ETH / share ratio.
with the lossy amount.
3. Next user withdrawing will withdraw more because users who will take the loss.

## Proof of Concept
Assume that there 100 ETH and 100 shares. A slashing event occurs and drops the deposits each. User A withdraws, and should take 100 ETH * 50 / 100 == 50 ETH, but takes 90 ETH * 50 / 100 == 45 ETH instead due to the loss. it becomes 55 ETH. Now, when LIDO recovers from the slashing, the contract will remaining 45 ETH in the contract that were not withdrawn yet are worth 50 ETH much more than it should at the expense of the variable users who will take the loss.

## Recommendation
their initial deposit back and the variable users don't take losses.
