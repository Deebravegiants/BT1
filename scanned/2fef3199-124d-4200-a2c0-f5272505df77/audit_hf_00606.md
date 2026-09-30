# [H] H-01 | Working With Stale State Can Cause Invalid Delegation Rights

## Summary
Severity: High
Contest weight: 0.2945
Dataset id: 2105
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user wants to update delegate rights on the base chain or mint an NFT on the shadow chain
they call lzread. However in lzread we use EVMCallComputeV1 with the current timestamp.
Meanwhile in lzmap we rely on a reading state that could potentially be outdated. This is because
the state is based on the timestamp set in EVMCallComputeV1 and by the time _executeMessage is
called that state may no longer be accurate.
Let's take example: (lzread from Base chain to Shadow chain). Initially, an NFT is locked on the base
chain but unlocked and owned by User A on Optimism, with lzRead delegating rights to User A. At
timestamp x, someone calls lzRead, and while the owner on Optimism has changed to User B, the
base chain still lists delegatedOwners[collectionAddress][tokenId] as User A at timestamp x.
At a later timestamp y, another lzRead call occurs, and now the owner on Optimism is User C, the
base chain still lists delegatedOwners[collectionAddress][tokenId] as User A at timestamp y. When
processing these updates, delegation rights are transferred from User A to User B for the ﬁrst call
and from User A to User C for the second call, leaving delegatedOwners[collectionAddress][tokenId]
set to User C. This creates an issue where both User B and User C have delegation rights, as the
delegation for User B cannot be properly revoked.

## Recommendation
To mitigate this issue, we should avoid reading staleOwner in lzmap. Instead we should read the
previous owner in _updateOwnership.
