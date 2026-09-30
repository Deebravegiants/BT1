# [M] M-07 | Unfair Reward Distribution On Donation Update

## Summary
Severity: Medium
Contest weight: 0.1160
Dataset id: 2028
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The donationPart can be updated with the increaseDonation function. This update will probably lead to an unfair distribution of rewards: • Current donationPart is 10% • Alice & Bob are the only stakers and deposit the same amt of funds • y amt of rewards are accumulated • Bob claims his part of the rewards and receives y/2*0.1% of the accumulated rewards • One block later the donation amt is increased to 20% • Alice claims her part of the rewards and receives y/2*0.2% of the accumulated rewards Now one staker received double the rewards for depositing the same amount of funds over the same period of time. Both should receive 10% of the accumulated rewards up to the point of changing the donationPart and 20% after that.

## Recommendation
Use an accumulator calculation to distribute the rewards to the users and remove the protocol and owner share directly in the _updateVester function.
