# [M] Potential underflow on userAmountStaked[token][msg.sender] in _withdraw

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-floatcapital
Published: 2021-08-10
Source: https://github.com/code-423n4/2021-08-floatcapital-findings/issues/45
Type: code-finding

## Details
# Handle

0xImpostor


# Vulnerability details

## Impact

Underflowing `userAmountStaked[token][msg.sender]` once will let me exploit the entire token balance in the Staker contract. This can only be exploited if marketUnstakeFee_e18 is ≥ 50%.

## Proof of Concept

1. Admin sets `marketUnstakeFee_e18` for this marketIndex at 60%.
2. Stake 1 token
3. Try and withdraw 2 tokens.
4. Line [933](https://github.com/code-423n4/2021-08-floatcapital/blob/main/contracts/contracts/Staker.sol#L933) will underflow
5. Line 937 will transfer 1.2 token to the treasury and line 938 will transfer 0.8 tokens back to me. Both lines will pass because Staker.sol contains funds from other users as well.
6. Withdraw successful and `userAmountStaked[token][msg.sender]` successfully underflowed to a large number.

## Tools Used

manual analysis

## Recommended Mitigation Steps

check that amount to withdraw is less than or equal to amount staked.
