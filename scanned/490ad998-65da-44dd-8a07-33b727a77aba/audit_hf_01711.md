# [C] C-1 Bypassing KYC in KintoWallet

## Summary
Severity: Critical
Contest weight: 0.2623
Dataset id: 9336
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• KintoWallet.sol#L204
A KintoWallet can have from one to three owners and have different signer policies. _validateSignature() and resetSigners() check KintoID only for the owner[0], which allows setting up a KintoWallet in such a way that it can be used by a user without a KintoID. To do this, a hacker first obtains a KintoID and KintoWallet. This is done either through a fake or stolen ID, or by stealing someone else's private key. Next, the hacker sets a 2/3 signature scheme in the KintoWallet and sets owner[0] to a person who has passed KYC and is not connected to the hacker. For example, they set Vitalik Buterin's account as owner[0]. The owner[1] and owner[2] accounts are the hacker's regular EOAs (Externally Owned Accounts) without KintoID. Now, the KintoWallet is in no way tied to the original account that created it, and the revocation or invalidation of the original owner's KintoID does not affect it. The hacker can use the KintoWallet, as they own 2/3 of the signatures, and the _validateSignature() function checks the KYC of only the first owner, who, in our example, is Vitalik Buterin.

## Recommendation
We recommend that in the _validateSignature() function, instead of checking the KYC of the first owner, each signature be simply counted valid only if its owner had a KintoID.
