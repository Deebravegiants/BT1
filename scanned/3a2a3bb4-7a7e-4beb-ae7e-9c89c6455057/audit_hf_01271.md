# [M] Plugin or target with selfdestruct

## Summary
Severity: Medium
Contest weight: 0.1377
Dataset id: 5949
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Until the 'Cancun' upgrade scheduled for later this year, whenever a delegatecall is made to a target contract or plugin that would do a SELFDESTRUCT the proxy would be destroyed at the end of the transaction and all ETH in the proxy would be sent to the address designated in the SELFDESTRUCT call. This would obviously be problematic but would also mean that the current owner of the proxy could not create a new proxy as the registry's proxies mapping for the user still points to the destroyed proxy address. After the upgrade, the selfdestruct opcode will not destroy the proxy contract but still send the ETH to the designated address. Although target and plugin contracts are gated by the plugins and permissions access control mechanisms it is still possible for an owner to unsuspectedly call a contract that selfdestructs.

## Recommendation
There's no easy way to detect whether a selfdestruct has been called in the delegatecall, but this does emphasize the need to assure target and plugin contracts are well vetted before being used. An optional (specified during the proxy's creation) allow list with audited target contracts could be used to aid in this assurance.
