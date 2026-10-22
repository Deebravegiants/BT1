# [M] Missing ifNotEmergencyState Modifier

## Summary
Severity: Medium
Contest weight: 0.1017
Dataset id: 15201
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The system contains an emergency mode which pauses functionality across multiple contracts. This emergency mode can be activated manually or through the discovery of a soundness bug to protect assets during a security incident. Most importantly, functionality for the claimAsset() and claimMessage() functions is paused when the emergency state is active. For consistency, bridgeAsset(), bridgeMessage() and bridgeMessageWETH() are also meant to be paused. However, for these latter two functions the ifNotEmergencyState modifier is missing, meaning that they will continue to function when the emergency state is active.

## Recommendation
It is recommended to add the ifNotEmergencyState modifier to bridgeMessage() and bridgeMessageWETH() functions in PolygonZkEVMBridgeV2.sol.
