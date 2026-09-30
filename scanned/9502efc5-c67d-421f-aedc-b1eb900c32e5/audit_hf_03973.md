# [M] Migration transactions executed out of order

## Summary
Severity: Medium
Contest weight: 0.1083
Dataset id: 20337
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The following migration calls have the potential to be executed out of order locking the new L2 DAO:
• deploy
• callMetadataRenderer
• renounceOwnership
ie if a DAO is deployed and then ownership is immediately renounced without the required metadata renderer calls the DAO will have no metadata set and any Token.mint calls will revert with a metadata error. a malicious actor can watch for deploy calls and block any migrated DAOs by immediately relaying the renounceOwnership call before any callMetadataRenderer calls. this issue occurs because the L2CrossDomainMessenger has no sense of ordering and the relayMessage calls can be called in any order. as long as deploy has been called the renounceOwnership call will succeed.

## Recommendation
No recommendation available
