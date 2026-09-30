# [M] Incorrect asset owner address may be emitted.

## Summary
Severity: Medium
Contest weight: 0.1271
Dataset id: 17513
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AssetReceived event emitted in onERC721Received may use an incorrect owner address if additional data is sent. The AssetReceived event in onERC721Received is emitted when an asset is received in the vault and its first parameter indicates the address which will be the beneficial owner. However, the event emission always uses the from parameter of onERC721Received as the beneficial owner. This may not be the case when additional data is sent with a beneficialOwner different from the from parameter for entitlement registration. This may mislead protocol user interfaces and offchain monitoring systems to misinterpret the actual beneficial owner and cause confusion, flagging of alerts or DoS.

## Recommendation
Use a different owner variable in the event emit which is set to from address or the decoded beneficial owner (when additional data is sent) accordingly. Use getBeneficialOwner to specify the operator https://github.com/hookart/protocol/pull/54 The fix is applied to the incorrect emit argument. It should be applied to the first `from` argument and not to the second one. https://github.com/hookart/protocol/pull/73 Verified fix.
