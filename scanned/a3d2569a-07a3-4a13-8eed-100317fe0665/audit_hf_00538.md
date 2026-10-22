# [M] M-12 | Burned Tokens Minted Arbitrarily

## Summary
Severity: Medium
Contest weight: 0.0983
Dataset id: 1996
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The NFTShadow contract makes incorrect assumptions about access control on minting. On an unlocked chain, after a token is burned, it remains unlocked. While unlocked it is possible for any user to to re mint(), updateOwnership() and steal delegations on other chains. In the comments "Only the Beacon contract can mint tokens, enforced by _beforeTokenTransfer". However the condition is actually as follows: if (msg.sender = BEACON_CONTRACT_ADDRESS) if (tokenIsLocked(tokenId)) revert CallerNotBeacon(); // if not beacon and locked} // if you are beacon, or unlocked

## Recommendation
If the msg.sender is not the BEACON_CONTRACT_ADDRESS and the token is unlocked, we will be able to mint to any recipient. After minting, we can updateOwnership on any other chain to steal delegation rights.
