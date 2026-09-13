# [M] Loopring incident: Loopring has appeared a serious front-end error, the private key material is set within a range of 32-bit integer, you can find al

## Summary
Severity: Medium
Target: Loopring
Loss: -
Attack method: System design defect
Published: 2020-05-07
Source: https://medium.loopring.io/loopring-exchange-frontend-password-bug-postmortem-cf55ce7e0150
Type: slowmist-incident

## Details
Loopring has appeared a serious front-end error, the private key material is set within a range of 32-bit integer, you can find all user private key pairs by brute force method, due to the user's EdDSA key pair is actually limited to a space of 32-bit integer, the hacker can find out the EdDSA key pair of all users by brute force method. Affected by this, Loopring Exchange shut down for half a day for maintenance and upgrade.
