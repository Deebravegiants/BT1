# [C] C-01 | DoS Attack In Withdraw Function

## Summary
Severity: Critical
Contest weight: 0.2275
Dataset id: 21954
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdraw function in the PerpetualVault contract allows users to specify a recipient when
withdrawing collateral.
The internal _withdraw function is then called to withdraw funds from GMX if the position is open.
Once withdrawn, the collateral tokens are transferred to the user-speciﬁed recipient address to
complete the withdrawal ﬂow. No other actions are permitted until this process is completed.
This allows a malicious actor to perform the following attack:
• Call the withdraw function with the recipient set to a blacklisted USDC address.
• The afterOrderExecution function in the GmxUtils contract will revert when trying to send the
collateral (USDC) to the blacklisted address.
• The ﬂow variable will still be 3 (WITHDRAW) and _gmxLock set to true, preventing any further
actions.
This effectively causes a DOS attack by locking the contract in a state where no further actions can
be taken.

## Recommendation
Do not transfer tokens directly to the recipient, instead make the token claimable for them in a
separate transaction and store their claimable balance in a mapping.
