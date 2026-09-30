# [C] C-02 | Tokens Stuck In Proxyledger When Claiming Vesting

## Summary
Severity: Critical
Contest weight: 0.1733
Dataset id: 21585
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When claiming vested ORDER, the OmnichainLedgerV1 sends PayloadType.ClaimVestingRequestBackward message to the ProxyLedger. However, the payload validation in ProxyLedger does not implement the ClaimVestingRequestBackward payload and instead reverts. This will result in tokens being stuck forever in the ProxyLedger because they will be minted to the ProxyLedger when the endpoint's lzReceive gets executed and a compose message will be stored that will call the ProxyLedger. The said compose message will always revert and the user will lose their tokens.

## Proof of Concept
https://github.com/GuardianAudits/omnichain-ledger-1/pull/3/files

## Recommendation
Change the ProxyLedger to support the ClaimVestingRequestBackward payload.
