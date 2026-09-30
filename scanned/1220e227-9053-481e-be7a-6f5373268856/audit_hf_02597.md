# [M] NativeVaultLib.validateWithdrawalCredentials() should return the actual balance of the validator

## Summary
Severity: Medium
Contest weight: 0.1181
Dataset id: 13974
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The effective balance of a validator is capped at 32 ETH. If a validator has more than 32 ETH, such as 64 ETH, getEffectiveBalanceWei() will return 32 ETH while its balance in BeaconProofsLib.validateBalance() would be 64 ETH.
As such, if NativeVault.validateWithdrawalCredentials() is called to register a validator that holds more than 32 ETH, only 32 ETH worth of shares will be minted to the nodeOwner and added to totalRestakedETH. The remaining shares will only be minted in the next snapshot.
This causes the number of shares held by the nodeOwner to be temporarily lower than their actual ETH balance until the next snapshot. Additionally, the shares that have not been minted cannot be slashed.

## Recommendation
Consider specifying restakedBalanceWei as the validator's actual balance here, using validateBalance().
Karak: Acknowledged. The excess ETH balance isn't restaked so node owners won't be getting rewards for them, so it's fine if it can't be slashed.
