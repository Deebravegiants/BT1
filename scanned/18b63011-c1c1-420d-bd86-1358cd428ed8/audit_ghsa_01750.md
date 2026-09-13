# [H] Holder can generate proof of ownership for credentials it does not control in vp-toolkit

## Summary
Severity: High
Advisory: GHSA-ff5x-w9wg-h275
Ecosystem: npm
Published: 2020-03-06
Source: https://github.com/advisories/GHSA-ff5x-w9wg-h275
Type: github-advisory

## Affected
- npm: `vp-toolkit` — affected >=0 <0.2.2

## Details
### Impact
The [`verifyVerifiablePresentation()`](https://github.com/rabobank-blockchain/vp-toolkit/blob/master/src/service/signers/verifiable-presentation-signer.ts#L97) method check the cryptographic integrity of the Verifiable Presentation, but it does not check if the [`credentialSubject.id`](https://github.com/rabobank-blockchain/vp-toolkit-models/blob/develop/src/model/verifiable-credential.ts#L150) DID matches the signer of the VP proof.

The **verifier** is impacted by this vulnerability.

### Patches
Patch will be available in version 0.2.2.

### Workarounds
- Compute the address out of the `verifiablePresentation.proof.n.verificationMethod` using `getAddressFromPubKey()` from `crypt-util@0.1.5` and match it with the `credentialSubject.id` address from the credential.

### References
[Github issue](https://github.com/rabobank-blockchain/vp-toolkit/issues/14)

### For more information
If you have any questions or comments about this advisory:
* Discuss in the existing [issue](https://github.com/rabobank-blockchain/vp-toolkit/issues/14)
* [Contact me](https://github.com/rabomarnix)

## References
- https://github.com/rabobank-blockchain/vp-toolkit/security/advisories/GHSA-ff5x-w9wg-h275
- https://github.com/rabobank-blockchain/vp-toolkit/issues/14
- https://github.com/rabobank-blockchain/vp-toolkit/commit/18a7db84d3265c6ffa10ef63eb37ae1bd4ba192b
