# [M] M-05 | Staking esOrder Without Balance

## Summary
Severity: Medium
Contest weight: 0.1131
Dataset id: 21578
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ProxyLedger allows users to stake ORDER or esORDER. When the isEsOrder flag is set to true, users will effectively stake esORDER on the OmnichainLedgerV1 contract, but will also be charged ORDER tokens, due to the fact that vaultSendToLedger will deduct the staked amount from the user balance. Therefore, user will end up with an esORDER stake, and ORDER tokens will be sent to the LedgerOCCManager contract. Although user will be able to unstake, vest and re-claim the ORDER tokens, this is an unexpected behavior as esORDER staking should not be triggered directly. Additionally, if future upgrades give more reward weight to esORDER staking, users will be able to game the system by creating an esORDER stake with ORDER tokens.

## Recommendation
Always use LedgerToken.ORDER in the ProxyLedger stake() and remove the isEsOrder param.
