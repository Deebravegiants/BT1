# [H] Rewards cannot be withdrawn

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-07
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/26
Type: code-finding

## Details
# Email address

mail@cmichel.io


# Handle

@cmichelio


# Eth address

0x6823636c2462cfdcD8d33fE53fBCD0EdbE2752ad


# Vulnerability details

The rewards for a recipient in `IncentiveDistribution.sol` are stored in the storage mapping indexed by recipient `accruedReward[recipient]` and the recipient is the actual margin trader account, see `updateAccruedReward`.

These rewards are supposed to be withdrawn through the `withdrawReward` function but `msg.sender` is used here instead of a `recipient` (`withdrawer`) parameter.
However, `msg.sender` is enforced to be the incentive reporter and can therefore not be the margin trader.



# Impact

Nobody can withdraw the rewards.


# Recommended mitigation steps

Remove the ` isIncentiveReporter(msg.sender)` check from `withdrawReward` function.
