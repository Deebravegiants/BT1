# [M] There should be only one Alchemist and yield token per Transmuter

## Summary
Severity: Medium
Contest weight: 0.1511
Dataset id: 4233
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After discussions with the team, we concluded that the correct design is to make Transmuters and Alchemists one-to-one. In Alchemix v2, having multiple underlying tokens was handled by having different Alchemists for each underlying yield token. In v3, this diversity of collateral is handled at the vault level, so that the yield token the Alchemist deals with can consist of any basket of underlying tokens the controlling DAO authorizes, through the managed Euler Eearn vault. Hence the need for multiple Alchemists per synthetic token (and hence per Transmuter) goes away.
The current design would not be able to correctly handle several Alchemists, since each Transmuter has only one staking graph, which the Alchemist(s) query to determine how much to earmark. If there were several Alchemists they would earmark extra funds for each other.
There is also a related issue with several alchemists, reported with the title "Incorrect index reassignment in removeAlchemist prevents future removals".

## Recommendation
Redesign the Transmuter to use only one Alchemist and one yield token. Remove the alchemist and yieldToken parameters from createRedemption(). Also remove these fields from the StakingPosition struct.
