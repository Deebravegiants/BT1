# [M] M-04 | NFT Owner Can Cause exclusiveOwnerByRights() Call To Revert

## Summary
Severity: Medium
Contest weight: 0.2462
Dataset id: 2089
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
unlockedExclusiveOwnerByRights() gets called by an LayerZeroV2 DVN off chain to read the new
owner of a NFT from a remote chain. Based on certain conditions the function will make a internal
call wrapped in a try catch block to the exclusive delegate resolver with the aim to return the address
to which the owner of the NFT have delegated and return it as the new owner instead.
IExclusiveDelegateResolver(EXCLUSIVE_DELEGATE_RESOLVER_ADDRESS).exclusiveOwnerByRights
() can loop over all outgoingDelegations of a particular owner of an NFT while it loads all in memory,
and performs checks in a loop. An owner on a remote chain could create/have thousands of active
delegations via IDelegateRegistry with different delegation type than ERC721.
When the off chain read request is processed
IExclusiveDelegateResolver(EXCLUSIVE_DELEGATE_RESOLVER_ADDRESS).exclusiveOwnerByRights
() inside unlockedExclusiveOwnerByRights() will loop for a very long time and will consume a lot of
gas. Off chain calls do not consume gas but they still simulate the consumption of gas in order to
revert if such off chain call loops for ever or is too computationally expensive like reaching the block
gas limit or some other limit set by the node.
Seems like the owner of the NFT will not be able to make unlockedExclusiveOwnerByRights() to
revert, which would be considered a critical issue since it will block future read requests from being
executed, because Layer Zero sets a 300M gas limit on such off chain view calls and second
because the inner call is wrapped in a try catch block. 63/64 part of the gas would be forwarded to
the internal call and the rest 1/64 would be suﬃcient to ﬁnish the rest of the function.
The impact of this would be that the read request will retrieve the actual owner of the NFT instead of
the delegated address and that the off chain services will more time to process the request since it
might be more computationally intensive. This could harm the owner of the NFT or the systems that
integrate and base their protocol logic on the result of the read request.

## Recommendation
Users and protocol that integrate with the system should be informed for this possible scenario.
