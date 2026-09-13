# [M] 6.3 Frontrun cancelDeposit()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 4 Code Corrected

After L1->L2 message cancellation has been initiated using
L1DAIBridge.startDepositCancellation() and the time delay has passed,
L1DAIBridge.cancelDeposit() can be used to complete the cancellation and retrieve the DAI.

The caller of the function must provide the details to retrieve the message (the amount, the l2Recipient
and the nonce) and as parameter l1Recipient any address to receive the funds on L1.

There is no access control, the first caller can retrieve the DAI to any address.

Code corrected:

msg.sender is now included in payload of deposit(), startDepositCancellation() and
cancelDeposit(). Hence, a successful cancellation requires that the same msg.sender in all three
calls of the process. Otherwise, the payload would be different.

```
payload[3] = uint256(uint160(msg.sender));
StarkNetLike(starkNet).cancelL1ToL2Message(l2DaiBridge, DEPOSIT, payload, nonce);
```
