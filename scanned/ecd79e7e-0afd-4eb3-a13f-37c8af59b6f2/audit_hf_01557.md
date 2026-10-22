# [M] Centralization risk that causes fund loss or lock

## Summary
Severity: Medium
Contest weight: 0.1392
Dataset id: 8335
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are multiple roles that are crucial for the protocol to work properly like the off-chain bot that updates AUM and the price setter role. If these roles comprised or work expectedly then contract crucial features would not work and users may lose funds. For example:
1. If an off-chain AUM updater bot is comprised then the attacker can increase/decrease AUM by 2% in each block, so after 10min can increase AUM by 150% and practically withdraw all of the contract funds. To avoid this, the code should add more limits for AUM changes, like don't let AUM be changed more than 10% in 5 min.
2. If an off-chain price setter is comprised, then it can set the wrong manual price for tokens and the attacker can steal protocol funds by interacting with the protocol. To avoid this the min/max limit price for each token should be updated frequently so the manual price setter can't cause more damage.

## Recommendation
Add max/min limit for what off-chain operator can set and also update them frequently. Also add longer period price change detection, for example, don't let AUM be changed more than 10% in 5 min.
