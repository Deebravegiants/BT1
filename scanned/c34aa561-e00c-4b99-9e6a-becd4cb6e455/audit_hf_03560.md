# [M] LGR-3 | User Can Withdraw Entire Collateral When Open Position

## Summary
Severity: Medium
Contest weight: 0.1333
Dataset id: 19362
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Before creating a position, a user is required to deposit a balance sufficient for their position size. Upon the call to executeWithdrawAction, there is validation that the withdraw amount is not greater than the balance. However, there is no validation at the contract level in the executeWithdrawAction function that restricts a user from withdrawing their entire balance once they have an open position. If a user’s position is in loss, the user could simply withdraw their entire collateral and not risk losing any of their balance during settlement. This terribly disrupts the operations of the protocol as funds won’t be available to pay profitable traders.

## Proof of Concept
https://github.com/GuardianAudits/OrderlyEVMContractsSuite/blob/4e216c2befe63c5379059f9359a7b3a0da008a71/test/GuardianPOC.t.sol#L183

## Recommendation
Before allowing a withdrawal, consider validating that the position will not be in a liquidatable state on chain. This may require passing a price with the WithdrawData.
