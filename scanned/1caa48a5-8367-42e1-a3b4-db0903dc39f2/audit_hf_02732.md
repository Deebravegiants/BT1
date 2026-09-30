# [M] Global house fee modification affects existing bets

## Summary
Severity: Medium
Contest weight: 0.1502
Dataset id: 14913
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The EnhancedSportsPrediction::setHouseFee function allows the owner to change the global house fee, which affects all existing bets. This can lead to unexpected changes in payout calculations for users who have already placed bets. More critically, the house fee calculation occurs in two separate places (EnhancedSportsPrediction::resolveCondition and EnhancedSportsPrediction::claimPayout), creating a potential inconsistency when the fee changes between these operations. This creates two significant impacts:
1. Users receive less than expected: If the house fee increases between condition resolution and payout claiming, users will receive lower payouts than they should based on the fee at the time of resolution.
2. Funds get trapped in the contract: The inconsistency creates a situation where totalFeesCollected doesn't match the actual fees collected from users. This breaks the economic integrity of the protocol and can result in funds permanently locked in the contract.

## Recommendation
Extend the Condition struct to host a houseFee field. Store the house fee within each Condition struct at the time of creation and use this stored fee for payout calculations in resolveCondition and claimPayout functions.
