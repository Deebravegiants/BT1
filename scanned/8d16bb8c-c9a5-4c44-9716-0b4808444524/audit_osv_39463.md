# [M] Janssen Project: JWE Request Object Signature Verification Bypass in jans-auth-server

## Summary
Severity: Medium
Advisory: CVE-2026-45795
Aliases: GHSA-r3gj-4pj2-9j3j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-45795
Type: osv

## Details
The Janssen Project is an open-source identity and access management (IAM) platform. Prior to 2.0.0, jans-auth-server accepts unsigned JWE request objects because JwtAuthorizationRequest skips inner signature validation when jwe.getSignedJWTPayload() returns null, and AuthzRequestService.processRequestObject() does not reject the unrecognized RSA-OAEP algorithm when forceSignedRequestObject=true. This issue is fixed in version 2.0.0.

## References
- https://github.com/JanssenProject/jans/releases/tag/v2.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45795.json
- https://github.com/JanssenProject/jans/security/advisories/GHSA-r3gj-4pj2-9j3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-45795
- https://github.com/JanssenProject/jans/commit/0cdd214870ee30eb2186261f21c85b9e9fc63b5c
- https://github.com/JanssenProject/jans/pull/13438
