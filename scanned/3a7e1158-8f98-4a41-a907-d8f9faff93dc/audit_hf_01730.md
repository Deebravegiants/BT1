# [M] LossofRewardsDuetoHardcodedZeroAddressasa _refreral

## Summary
Severity: Medium
Reporter: atharv_181
Contest weight: 0.2078
Dataset id: 9443
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Node Operators won’t receive referral rewards for depositing ETH into Lido. When staking ETH with Lido and depositing stETH into the bond, the process calls CSBondCore::_depositETH() to deposit ETH into Lido. However, since the referral address is passed as zero, no referral rewards are earned.
The Lido Rewards Share Program started a referral initiative to increase participation in staking via Lido. Participants can refer others to Lido, earning a share of rewards based on the staked amounts of those they refer.
Participants can earn referral rewards proportional to the staked amount of those they refer. The exact earnings depend on how much ETH the referred users stake and the duration they keep their assets staked.
Let’s say prior to enrollment, the amount of ETH staked through Participant A’s products and services is 60,000 ETH and the Committee agreed to a 25% Rewards Share Percentage.
If as a result of the 60,000 ETH stake a middleware usage fee in the amount of 1,000 ETH is programmatically collected, Participant A would receive 250 ETH as their share (25% of 1000 ETH).
This reward-sharing continues for each ETH staked, starting from the date each ETH is staked, and generally lasts for 12 months. If Participant A decides to stake additional ETH during this period, each new ETH will also earn rewards for 12 months from the date it was staked.
Hardcoding the referral address to address(0), the reward amount is lost.
More info about the referral program - Lido Referral Program
Transaction with Referral Address Provided - Transaction Link
Figure 1: Input Data

## Recommendation
Referrals should be distributed to all node operators proportionally to bond shares.
