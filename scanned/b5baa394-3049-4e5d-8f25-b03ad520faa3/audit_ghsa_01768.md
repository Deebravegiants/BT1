# [H] Holder can (re)create authentic credentials after receiving a credential in vp-toolkit

## Summary
Severity: High
Advisory: GHSA-p94w-42g3-f7h4
Ecosystem: npm
Published: 2020-03-06
Source: https://github.com/advisories/GHSA-p94w-42g3-f7h4
Type: github-advisory

## Affected
- npm: `vp-toolkit` — affected >=0 <0.2.2

## Details
### Impact
The [`verifyVerifiableCredential()`](https://github.com/rabobank-blockchain/vp-toolkit/blob/master/src/service/signers/verifiable-credential-signer.ts#L57) method check the cryptographic integrity of the Verifiable Credential, but it does not check if the [`credential.issuer`](https://github.com/rabobank-blockchain/vp-toolkit-models/blob/develop/src/model/verifiable-credential.ts#L129) DID matches the signer of the credential.

The **verifier** is impacted by this vulnerability.

### Patches
Patch will be available in version 0.2.2.

### Workarounds
In case you trust certain issuers for certain credentials as a verifier, trust the issuer&#39;s public key from the `credential.proof.verificationMethod` field.

### References
[Github issue](https://github.com/rabobank-blockchain/vp-toolkit/issues/13)

### For more information
If you have any questions or comments about this advisory:
* Discuss in the existing [issue](https://github.com/rabobank-blockchain/vp-toolkit/issues/13)
* [Contact me](https://github.com/rabomarnix)

## References
- https://github.com/rabobank-blockchain/vp-toolkit/security/advisories/GHSA-p94w-42g3-f7h4
- https://github.com/rabobank-blockchain/vp-toolkit/issues/13
- https://github.com/rabobank-blockchain/vp-toolkit/commit/6315936d1d7913fd116fa51a0dbbd29d82c0ce17
