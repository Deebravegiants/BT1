# [M] M-01 | Working With Stale State Can Cause DoS

## Summary
Severity: Medium
Contest weight: 0.1836
Dataset id: 2086
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user wants to update delegate rights on the base chain or mint an NFT on the shadow chain
they call lzread. However in lzread we use EVMCallComputeV1 with the current timestamp.
Meanwhile in lzmap we rely on a reading state that could potentially be outdated. This is because
the state is based on the timestamp set in EVMCallComputeV1, and by the time _executeMessage is
called, that state may no longer be accurate.
Example: (lzread from Shadow chain to Shadow chain or Base chain)
For now Shadow chain to Shadow chain example it taken. ApeChain is Shadow chain 1 and Arbitrum
is Shadow chain 2. Initially, an NFT is locked on the Arbitrum but unlocked and owned by User A on
ApeChain, with lzRead delegating rights to User A. At timestamp x, someone calls lzRead from
Arbitrum, and while the owner on ApeChain has changed to User B, the Arbitrum chain lists
staleOwner as User A at timestamp x.
At a later timestamp y, another lzRead call occurs from Arbitrum, and now the owner on ApeChain is
User C, the Arbitrum chain lists staleOwner as User A at timestamp x. When processing these
updates, ownership is transferred from User A to User B for the ﬁrst call because User A was owner
and from User A to User C ownership transfer for the second call will not work because Current
owner will be User B. This causes DOS.

## Recommendation
To mitigate this issue, we should avoid reading staleOwner in lzmap. Instead, we should read the
previous owner in _updateOwnership.
