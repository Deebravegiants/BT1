# [M] joserfc claim-validation bypass via array-typed single-string claims (iss/sub/jti)

## Summary
Severity: Medium
Advisory: CVE-2026-75509
Aliases: GHSA-r74j-q665-7rpj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-75509
Type: osv

## Details
joserfc is a Python library that provides an implementation of several JSON Object Signing and Encryption (JOSE) standards. Prior to version 1.7.3, JWTClaimsRegistry applies membership matching to list-valued iss and sub claims, allowing an array-valued iss that contains the expected issuer to pass an intended equality check and enabling issuer-validation bypass. This issue is fixed in version 1.7.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75509.json
- https://github.com/authlib/joserfc/security/advisories/GHSA-r74j-q665-7rpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-75509
- https://github.com/authlib/joserfc/commit/76ee6a59bf5773c0af00b99076c5e199031f97f1
