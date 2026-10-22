# [M] Any user can claim an unlimited amount of

## Summary
Severity: Medium
Contest weight: 0.4024
Dataset id: 23022
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, there is no validation performed in VouchFaucet.sol when claimVouch is
called. This is highly dangerous as any untrusted user can increase their vouch and
perform malicious borrows, stealing from the contract's stake.
As we can see in the claimVouch function there is no validation performed and it
can be called by any address:
```solidity
function claimVouch() external {
    IUserManager(USER_MANAGER).updateTrust(msg.sender, uint96(TRUST_AMOUNT));
    emit VouchClaimed(msg.sender);
}
```
In addition to that, the maximum amount of trust that any user can claim -
TRUST_AMOUNT can easily be bypassed by calling claimVouch, borrowing the entire
TRUST_AMOUNT and after that calling claimVouch again.
Malicious borrows can be made by untrusted users and the maximum amount that
can be vouched for a user can be bypassed, putting the contract's funds at risk of
being stolen.

## Recommendation
Only users approved by the owner should be able to call claimVouch and they
should not be able to claim more trust than TRUST_AMOUNT.
