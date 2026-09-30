# [M] Changing the bridging modules

## Summary
Severity: Medium
Contest weight: 0.2137
Dataset id: 1816
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Changing the module state parameter of RootMessageBridge and LeafMessageBridge contracts can cause the delivery of in-flight messages to always revert.
The RootMessageBridge and LeafMessageBridge contracts have the ability to change the module parameter via setModule functions.
63a33b963e3bdf76a1c871e6a6ecd7c5403d/superchain-contracts-private/src/bridge/CrossChainRegistry.sol#L45-L50
63a33b963e3bdf76a1c871e6a6ecd7c5403d/superchain-contracts-private/src/bridge/LeafMessageBridge.sol#L25-L29
During the module change, in case there exists a message which got transmitted from the root chain but haven't arrived on leaf chain then that in-flight message cannot be delivered on leaf chain. Delivery of that message will revert because all leaf chain operations validate that they are being called by latest leaf module.
c871e6a6ecd7c5403d/superchain-contracts-private/src/gauges/LeafGauge.sol#L192
Hence delivery of that in-flight message will revert on leaf chain.
Scenario:
1. A cross chain operation gets initiated via RootMessageBridge.sendMessage.
2. Owner of RootMessageBridge and LeafMessageBridge contracts changes the modules on both root and leaf chains.
3. The message from step 1 arrives to leaf chain but gets reverted.
This scenario can occur in real life when Velodrome decides to upgrade their currently active bridge modules.
Atomicity of cross-chain messages will get broken when a module upgrade is in progress.
The messages will get executed on root chain but will fail on leaf chain.

## Recommendation
It should be made sure that there are no in-flight messages during a module change.
There are cases when messages cannot be executed instantly on leaf chains (like messages waiting due to leaf chain's XERC20 buffer limits), those cases should also be taken care of.
One way of resolving this could be to have a message pause mechanism on RootMessageBridge so that the message bridging can be paused earlier to a module change upgrade.
