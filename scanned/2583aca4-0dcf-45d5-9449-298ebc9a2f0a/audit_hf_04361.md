# [C] C-04 | Inability To Transmit Messages To Vault Chain

## Summary
Severity: Critical
Contest weight: 0.2441
Dataset id: 21566
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LedgerOCCManager relays message requests from the OmnichainLedgerV1 to the vault chain using ledgerSendToVault. This function will call the orderTokenOft contract with the native fee and set LedgerOCCManager as the refund recipient. These relay requests will fail due to the fact that:
1. The ProxyLedger does not specify any msg.value sent to the lzCompose function during execution. bytes memory options = OptionsBuilder.newOptions.addExecutorLzReceiveOption(_oftGas, 0).addExecutorLzComposeOption(0, _dstGas, 0);
2. Owner can't fund LedgerOCCManager with native currency, as there is no receive function.
3. If there are any excess fees, the refund transaction will revert. Therefore, LedgerOCCManager has no native currency to pay the message fees, preventing users to execute any function on ledger chain with a backward message.

## Proof of Concept
https://github.com/GuardianAudits/omnichain-ledger-1/pull/4/files

## Recommendation
If the message fee is meant to be paid by Orderly, add a receive function to LedgerOCCManager contract to allow deposits and refunds to be processed and a privileged withdraw function. Otherwise, consider specifying the addExecutorLzComposeOption with the msg.value that needs to be sent by the executor in order to pay for the backward message.
