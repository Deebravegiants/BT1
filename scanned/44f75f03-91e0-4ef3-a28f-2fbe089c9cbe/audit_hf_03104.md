# [M] Incorrect asset withdrawal address emitted.

## Summary
Severity: Medium
Contest weight: 0.1390
Dataset id: 17512
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AssetWithdrawn event emitted in clearEntitlementAndDistribute uses an incorrect withdrawal address. The AssetWithdrawn event in clearEntitlementAndDistribute is emitted when an asset is withdrawn from the vault and its second parameter indicates the address to which the asset is sent upon withdrawal. clearEntitlementAndDistribute takes a receiver parameter which indicates the intended receiver of the asset to which safeTransferFrom sends the asset. However, the AssetWithdrawn event emitted uses msg.sender (operator) instead of the receiver address (beneficialOwner) for the ‘to’ address argument, when msg.sender need not be equal to the receiver address. This may mislead protocol user interfaces and offchain monitoring systems to misinterpret the recipient (operator vs beneficial owner) of asset distribution to cause confusion, flagging of alerts or DoS.

## Recommendation
Change emit AssetWithdrawn(assetId, msg.sender, assets[assetId].beneficialOwner); To emit AssetWithdrawn(assetId, receiver, assets[assetId].beneficialOwner); Use receiver instead of msg.sender in AssetWithdrawn event. https://github.com/hookart/protocol/pull/50 Ok.
