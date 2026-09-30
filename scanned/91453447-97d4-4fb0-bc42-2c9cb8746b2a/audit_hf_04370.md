# [M] M-04 | Vesting Claims DoS’ed With OFT Token Update

## Summary
Severity: Medium
Contest weight: 0.1448
Dataset id: 21577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
orderTokenOft is set in the OmnichainLedgerV1 initialize function, but admin can use setOrderTokenOft to update this token address at a later stage. There are a couple of issue that arise when performing this update:
- LedgerOCCManager does not contain an admin function to update the orderTokenOft address. If address is updated on OmnichainLedgerV1 and not in LedgerOCCManager, users will still be able to stake with the old token address.
- LedgerOCCManager will hold orderTokenOft tokens sent from vault chains. If the token address is updated, any withdraw or claim will fail as the contract does not have balance of the new token.
- When users request vesting claims, the unclaimedOrderAmount will be sent to the orderCollector. In case admin updates the orderTokenOft, user claims will be DoS'ed as the contract may not have sufficient amount of the new token to transfer the collector.

## Recommendation
Avoid changing the orderTokenOft address. Alternatively, add setOrderTokenOft to the LedgerOCCManager contract or always read the updated address from the OmnichainLedgerV1. Be aware that same amount of OFT tokens should me minted as the previous OFT token balance in LedgerOCCManager to avoid issues with the stakes and vests.
