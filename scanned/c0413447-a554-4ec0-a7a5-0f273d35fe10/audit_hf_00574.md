# [H] H-03 | Lack Of Incentives For Users To Match Withdrawals

## Summary
Severity: High
Contest weight: 0.2990
Dataset id: 2036
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ExitVault contract, withdrawals are fulfilled by other users who match these requests, taking over their staking positions and receiving a portion of their shares as donation for helping them exit. This donation is used to incentivize others to fulfill their withdrawal requests. However, once all the esGMX tokens have been fully vested (i.e., the vault reaches maxVestableAmountGmx and maxVestableAmountGlp), the vault cannot vest additional esGMX tokens. At this point, new users have no incentive to match withdrawal requests because they can no longer benefit from the vesting rewards as no more esGMX will be converted into GMX. This creates a scenario where existing users who wish to withdraw are unable to do so unless they find someone willing to match their withdrawal request without the prospect of earning vesting rewards. As matching a withdrawal request would not yield any benefits to the new participant, it's unlikely anyone would agree to fulfill such requests, even with a donation. This situation resembles the old "King of the Ether" game, where users are effectively locked into the contract with no viable means of exiting their positions unless someone else takes their place. The only option left is to offer increasingly higher donations to entice someone to take over, leading to an impractical and potentially infinite loop without resolution.

## Recommendation
Introduce a mechanism that allows users to withdraw their tokens directly when the vault has reached its maximum vesting capacity.
