# [M] Privileged role and actions lead to centralization risks for users

## Summary
Severity: Medium
Contest weight: 0.1526
Dataset id: 6203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Several restricted/access-controlled functions across bridging logic affect critical protocol state and semantics, leading to centralization risk for users. Some examples are highlighted below:
• setTargetFunctionRole() can potentially allow an EOA or a malicious contract acting as LayerZeroAdapter to steal user NFTs.
• Abuse of sendMessageUsingERC20 / sendMessageUsingNative can occur by adding an EOA to the Bridge role, allowing messages to be sent without transferring NFTs to the Bridge.sol contract.
• Updating the s_bridge address through the updateBridge function can result in the loss of NFTs if a message is still in transit during the update.
• setEvmChainSetting can be used to disable an existing route while a message is in transit, which can lead to a temporary or permanent inability to deliver a message in the queue.

## Recommendation
Consider:
• Making certain configurations immutable and considering deploying newer versions if a change has to be effected.
• Enforce deterministic access-control measures and remove the AccessManager library from OpenZeppelin, which introduces opaque access controls.
• Documenting the privileged role and actions for protocol user awareness.
• Privilege actions affecting critical protocol semantics should be locked behind timelocks so users can decide to exit or engage.
• Following the strictest opsec guidelines for privileged keys, e.g., use of reasonable multi-sig and hardware wallets.
Sweep n' Flip: Acknowledged.
