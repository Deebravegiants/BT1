# [M] M-7 Wrong conditions in mint

## Summary
Severity: Medium
Contest weight: 0.1159
Dataset id: 7931
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Wrong conditions in mint (FantiumMinterV1.sol#L200):
if (
!hasRole(PLATFORMMANAGERROLE, msg.sender) ||
!hasRole(DEFAULTADMINROLE, msg.sender)
) {
require(isAddressKYCed(msg.sender), "Address not KYCed");
}
IFantiumNFT.Collection memory collection = fantiumNFTContract
.getCollection(_collectionId);
// sender must be on allow list or Admin or Manager if the collection is pause
if (
!hasRole(PLATFORMMANAGERROLE, msg.sender) &&
!hasRole(DEFAULTADMINROLE, msg.sender)
) {
require(
!collection.paused ||
isAddressOnAllowList(_collectionId, msg.sender),
"Purchases are paused and not on allow list"
);
}

## Recommendation
The correct (but not the optimal) form is to use the "&&" operator:
if (
!hasRole(PLATFORMMANAGERROLE, msg.sender) &&
!hasRole(DEFAULTADMINROLE, msg.sender)
)
But the best way would be to restrict privileges and disallow unnecessary access altogether:
require(isAddressKYCed(msg.sender), "Address not KYCed");
IFantiumNFT.Collection memory collection = fantiumNFTContract
.getCollection(_collectionId);
require(!collection.paused, "Purchases are paused");
