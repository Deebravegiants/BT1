# [M] If the royalties receiver it's a

## Summary
Severity: Medium
Contest weight: 0.3974
Dataset id: 23247
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function InfernalRiftAbove::claimRoyalties() can only be called by the receiver of the royalties:
```solidity
(address receiver,) = IERC2981(_collectionAddress).royaltyInfo(0, 0);
// Check that the receiver of royalties is making this call
if (receiver != msg.sender) revert CallerIsNotRoyaltiesReceiver(msg.sender, receiver);
```
This is fine for EOAs but is problematic if receiver is a contract that doesn't have a way to call InfernalRiftAbove::claimRoyalties(), as this would result in the receiver not being able to claim the royalties collected by NFTs bridged to L2. Internal pre-conditions External pre-conditions Attack Path If the royalties receiver is a smart contract that doesn't have a way to call InfernalRiftAbove::claimRoyalties() it's impossible to claim the royalties, which will be stuck.

## Recommendation
Allow royalties to be claimed to the receiver address by anybody when receiver is a smart contract.
