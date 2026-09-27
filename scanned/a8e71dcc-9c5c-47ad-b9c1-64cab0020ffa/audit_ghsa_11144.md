# [H] jose vulnerable to untrusted JWK header key acceptance during signature verification

## Summary
Severity: High
Advisory: GHSA-vm9r-h74p-hg97
CVE: CVE-2026-34240
CWE: CWE-347
Ecosystem: Pub
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-vm9r-h74p-hg97
Type: github-advisory

## Affected
- Pub: `jose` — affected >=0 <0.3.5+1

## Details
### Impact

A vulnerability in `jose` versions up to and including `0.3.5` could allow an unauthenticated, remote attacker to forge valid JWS/JWT tokens by using a key embedded in the JOSE header (`jwk`).  

The vulnerability exists because key selection could treat header-provided `jwk` as a verification candidate even when that key was not present in the trusted key store. Since JOSE headers are untrusted input, an attacker could exploit this by creating a token payload, embedding an attacker-controlled public key in the header, and signing with the matching private key.  

Applications using affected versions for token verification are impacted.

### Patches

Upgrade to `0.3.5+1` or later.

### Workarounds

Reject tokens where header `jwk` is present unless that `jwk` matches a key already present in the application's trusted key store.

### Resources

Fix commit: [fix: improved key resolution in JsonWebKeyStore](https://github.com/appsup-dart/jose/commit/b07799aac1f56a9a21483feac026272aab30cc5d)

## References
- https://github.com/appsup-dart/jose/security/advisories/GHSA-vm9r-h74p-hg97
- https://nvd.nist.gov/vuln/detail/CVE-2026-34240
- https://github.com/appsup-dart/jose/commit/b07799aac1f56a9a21483feac026272aab30cc5d
- https://github.com/appsup-dart/jose
