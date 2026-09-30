# [H] Claim Restriction Prevents Users

## Summary
Severity: High
Contest weight: 0.3050
Dataset id: 1753
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
from Claiming Multiple Epochs
Source:
After a user makes a claim, they are unable to claim rewards for subsequent epochs due
to a check that restricts claims based on prior activity.
The handleProofResult function includes a check that requires the claimed amount to be
zero (require(claim.amount == 0, "Already claimed reward.");). Once a user successfully
claims rewards, this condition prevents them from claiming for any future epochs, as
their claim amount is no longer zero.
Internal pre-conditions
External pre-conditions
Attack Path
For simplicity, let’s assume the distribution rewards are set to 100 blocks, with a total of
100 rewards to be distributed and blocksPerEpoch set to 20, resulting in 5 epochs. In this
scenario, the amountPerEpoch is 20. If Kate is eligible to claim for the entire period and,
at block 21, she claims rewards for blocks 0-20, the amount recorded in the
CumulativeClaim (in the mapping claimed) for Kate for this token and reward
distribution will be 20. If Kate attempts to claim rewards for any other epoch, her request
would revert due to the check: require(claim.amount == 0, "Already claimed reward."); as
claim.amount would be 20. Kate should be eligible to claim for other epochs, but she is
not. Github Link
Users are unable to claim rewards for multiple epochs after their initial claim, resulting in
missed opportunities to receive rewards. This restriction diminishes user engagement
and overall satisfaction with the protocol.

## Recommendation
No recommendation available
