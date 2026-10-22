# [C] C-01 | Messaging Channel Blocked By Locked Chain Reads

## Summary
Severity: Critical
Contest weight: 0.3196
Dataset id: 2005
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The unlockedExclusiveOwnerByRights function reverts for chains that have the NFT locked. However this will cause the read messaging channel for the OApp on that chain to be blocked, preventing all subsequent reads on the chain. This occurs because the DVNs cannot process the read request, producing an error of UnresolvableCommand which prevents the DVN from verifying their response for the nonce. When DVNs have not verified the response for a nonce, validation in the EndpointV2 contract prevents any subsequent messages for the OApp from being processed in lzReceive: [https://github.com/LayerZero-Labs/LayerZero-v2/blob/7da76840e41dc593d3c2007ce35b911b1d816b4b/packages/layerzero-v2/evm/protocol/contracts/MessagingChannel.sol#L138](https://github.com/LayerZero-Labs/LayerZero-v2/blob/7da76840e41dc593d3c2007ce35b911b1d816b4b/packages/layerzero-v2/evm/protocol/contracts/MessagingChannel.sol#L138) This produces a block of read messages on the chain which the invalid read request was triggered from. The delegate of the OApp can call the skip function on the endpoint in order to skip the affected nonce which cannot be veriﬁed and resume lzReceive processing. However with the commonality of reverts in the target unlockedExclusiveOwnerByRights the delegate will not successfully be able to unstuck the read channels, especially on chains where gas costs are high like Ethereum. As a result the ownership syncing feature is completely DoS'd by either malicious or normal use.

## Recommendation
Instead of reverting in the unlockedExclusiveOwnerByRights function when the token is locked on the target chain, consider returning a boolean value in addition to the exclusive owner address which indicates whether the chain is locked or not.
