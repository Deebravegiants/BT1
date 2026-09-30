# [H] H-02 | If Beacon Delegates To Address(0) It Will Be Permanent

## Summary
Severity: High
Contest weight: 0.2712
Dataset id: 2106
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Beacon can delegate to address(0) in case the owner on the remote chain have burned the NFT.
In this scenario the NFT remains unlocked and a read request from the base chain will set
delegatedOwners[collectionAddress][tokenId] to address(0). This will remove the active delegation
of the stale owner and will create a new delegation to address(0) via
IDelegateRegistry.delegateERC721.
There is another case where the owner of the NFT on the remote chain delegates to address(0) via
IDelegateRegistry.delegateERC721. Upon a read request the Beacon on the base chain will create an
active delegation to address(0) that it will not be able to remove ever again for this NFT since we
encounter this check in _updateDelegations() when the staleOwner is address(0): if (staleOwner =
address(0)) {.
This means that when the NFT gets a new owner on the remote chain from now on, the base chain
will have 2 active delegations. One to address(0) and one to the current owner. Having two active
delegations can confuse projects that implement logic for distributing rewards based on your
current active delegations (and split the rewards), require you to have 1 active delegation or does not
handle well delegation to address(0).

## Recommendation
Consider including a if (newOwner = address(0)) { check.
