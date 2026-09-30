# [M] Factory uses signature that do not have expi-

## Summary
Severity: Medium
Contest weight: 0.3898
Dataset id: 17770
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
NftPort can't remove license from user, once the signature was provided to it, without changing SIGNER_ROLE address. In Factory contract there are few methods that are called when signed by trusted signer. This is how the signature is checked:
```solidity
signedOnly(abi.encodePacked(msg.sender, instance, data), signature)
```
As you can see there is no any expiration time. That means that once, the signer has signed the signature for the user it can use it for the end of life. It's like lifetime license. The only option to remove the license from user is to revoke SIGNER_ROLE and set it to another account. But it's possible that the NFTPort will have a need to do that with current signer. License can't be removed.

## Recommendation
Add expiration param to the signature.
