# [M] Verification flaw in Solid identity-token-verifier

## Summary
Severity: Medium
Advisory: GHSA-xmh9-rg6f-j3mr
CWE: CWE-290
Ecosystem: npm
Published: 2021-03-12
Source: https://github.com/advisories/GHSA-xmh9-rg6f-j3mr
Type: github-advisory

## Affected
- npm: `@solid/identity-token-verifier` — affected >=0 <0.5.2

## Details
### Impact
#### Severity
Any Pod on a Solid server using a vulnerable version of the identity-token-verifier library is at risk of a spoofed Demonstration of Proof-of-Possession (DPoP) token binding. This vulnerability could give total and complete access to a targeted Pod.

#### Summary
A verification flaw in the implementation of the identity token verifier library (https://github.com/solid/identity-token-verifier) allows DPoP proofs to be spoofed. 

DPoP proofs are used to bind access tokens to a private key meant to be in sole possession of a specific user. Instead of verifying against the hash of an embedded public key, the library instead verifies against a field that an attacker can modify to spoof another user’s DPoP. 

A stolen DPoP proof, when used in the right context, therefore allows the rebinding of a DPoP-bound access token. Any attacker in possession of a targeted access token could build an attack environment to replay it on any Pod service with this vulnerability.  


### Patches
A new version 0.5.2 of identity-token-verifier fixes the verification: https://github.com/solid/identity-token-verifier/blob/7e18d86d65ee681e8ae912b6a032a1bae3cae570/src/lib/DPoP.ts#L25-L35

### Workarounds
None

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [identity-token-verifier](https://github.com/solid/identity-token-verifier/) repository.
* Email: info@solidproject.org

## References
- https://github.com/solid/identity-token-verifier/security/advisories/GHSA-xmh9-rg6f-j3mr
- https://github.com/solid/identity-token-verifier/commit/fbdeb4aa8c12694b3744cd0454acb826817d9e6c
- https://github.com/solid/identity-token-verifier/releases/tag/0.5.2
- https://www.npmjs.com/package/@solid/identity-token-verifier
