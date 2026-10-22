# [M] DOS for removal of delegates

## Summary
Severity: Medium
Contest weight: 0.5542
Dataset id: 8948
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The delegation system on vePeg.sol has the feature that MAX_DELEGATES is a hardcoded value. On the other hand, users can create locks with only 1 wei LP because _create_lock() only has this check require(_value > 0); Now, take this scenario: Alice owns vePeg_NFT_01 (with big weight) and she decides to delegate it to Malicious user. Malicious user back-runs Alice transaction and delegates to Alice a MAX_DELEGATES vePeg_NFT (only 1 wei LP). After a period, Alice will try to move her delegates of the vePeg_NFT_01 from Bob, but it will fail due to this requirement.
File: vePeg.sol#_moveAllDelegates
```solidity
require(
    dstRepOld.length + ownerTokenCount <= MAX_DELEGATES,
    "dstRep would have too many tokenIds"
);
```
The user is not able to remove his vePeg_NFT from the delegate for 52 Epochs. Anyone can deprive users of receiving any delegations with this attack.

## Recommendation
```solidity
//File: VotingEscrow.sol
require(
    dstRepOld.length <= MAX_DELEGATES,
    "dstRep would have too many tokenIds"
);
```
