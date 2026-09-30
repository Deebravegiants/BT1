# [H] Unset governor allows to steal both yield and gas refund

## Summary
Severity: High
Contest weight: 0.1609
Dataset id: 14008
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CrossDomainMessenger predeploy does not have its governor configured in Blast.sol. This means that if an attacker sends a message to L2 like shown below, then it would become the governor of the CrossDomainMessenger contract:
// `relayMessage` called with:
_target = Blast contract
selector = configure
_yieldMode = Automatic
Gasmode = CLAIMABLE
governor = Attacker
This allows them to claim:
1. Yield from the collected ETH in L2CrossDomainMessenger, if the relayMessage (temporarily) failed.
2. Gas for the L2CrossDomainMessenger.

## Recommendation
Add Blast contract to _isUnsafeTarget or initialize the predeploy with itself as the governor. Also, for all L2 contracts allowing arbitrary calls, consider setting some governor to prevent an attacker from taking control.
