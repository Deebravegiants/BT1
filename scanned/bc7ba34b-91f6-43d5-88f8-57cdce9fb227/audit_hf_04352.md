# [M] M-02 | Reheat Sniping

## Summary
Severity: Medium
Contest weight: 0.1200
Dataset id: 21511
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reheat function will buy YES and loop it when the random roll hits. However the random value is based upon the block.timestamp and block.prevrandao which are both deterministically available at the block in which the reheat transaction is recorded. In environments where front-running is possible, a malicious actor may create a contract which buys YES and reverts if the block.timestamp and block.prevrandao would not fulfill the random requirements. This way the attacker can detect owner transactions to reheat and frontrun them in the same block to buy YES right before the price increases as a result of the reheat. The attacker can then back run the reheat and sell their YES tokens if a reheat looping was performed for a risk free immediate profit.

## Recommendation
This is not an immediate concern on the Blast L2 network, however be sure to consider this risk before deploying to a network with high MEV activity.
