# [H] H-02 | [_acceptNonce](https://github.com/GuardianAudits/oft-team-1-pocs/blob/e8b7aad0b1e812be934e5c180f2a2569b044bb37/contracts/OrderAdapter.sol#L106C1-L115C6) Should Not Be Called

## Summary
Severity: High
Contest weight: 0.3185
Dataset id: 21581
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[OrderOFT](https://github.com/GuardianAudits/oft-team-1-pocs/blob/e8b7aad0b1e812be934e5c180f2a2569b044bb37/contracts/OrderOFT.sol#L82-L97) and [OrderAdapter](https://github.com/GuardianAudits/oft-team-1-pocs/blob/e8b7aad0b1e812be934e5c180f2a2569b044bb37/contracts/OrderAdapter.sol#L83C1-L98C6) allow the owner to burn, nilify, skip and clear nonces. When doing so, a call to _acceptNonce is initiated. This is problematic for:
- burning: The nonce to be burnt will always be less than the maxReceivedNonce. However, in ordered delivery the _acceptNonce function reverts if the specified nonce is not max + 1. This will result in burning not working when ordered delivery is turned on.
- nilifying: The _acceptNonce will let us nilify only the packet with nonce = max + 1. After nilifying the maxReceivedNonce will be set to the nilified nonce. Now even if the nilified package gets reverified, it will not be possible to execute it.
- clearing: If there is a need to clear a nonce which is bigger than maxNonce + 1, it will be impossible because of the ordered nonce. In addition, these actions can be initiated by a delegate address and not by the OFTApp directly. This will cause a discrepancy between the OrderOFT and LayerZero maxReceivedNonce and the messaging will be blocked because acceptNonce will always revert from this moment on.

## Recommendation
Do not call _acceptNonce when burning, nilifying, nor clearing. Furthermore, add a setter setMaxReceivedNonce to update the mapping as necessary and even consider passing a maxReceivedNonce argument in each of the functions which can be used to update the mapping during the execution of the owner functions. This is because since there can be multiple in-flight packets and one of them is burned/nulled/cleared, and now the order enforcement will lead to DoS. Furthermore, a delegate can burn/nullify/clear outside the Oapp so the setter is absolutely necessary.
