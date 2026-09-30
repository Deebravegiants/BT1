# [C] jwe: Missing AES-GCM authentication tag validation in encrypted JWEs

## Summary
Severity: Critical
Advisory: CVE-2025-54887
Aliases: GHSA-c7p4-hx26-pr73
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-08-08
Source: https://osv.dev/vulnerability/CVE-2025-54887
Type: osv

## Details
jwe is a Ruby implementation of the RFC 7516 JSON Web Encryption (JWE) standard. In versions 1.1.0 and below, authentication tags of encrypted JWEs can be brute forced, which may result in loss of confidentiality for those JWEs and provide ways to craft arbitrary JWEs. This puts users at risk because JWEs can be modified to decrypt to an arbitrary value, decrypted by observing parsing differences and the GCM internal GHASH key can be recovered. Users are affected by this vulnerability even if they do not use an AES-GCM encryption algorithm for their JWEs. As the GHASH key may have been leaked, users must rotate the encryption keys after upgrading. This issue is fixed in version 1.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54887.json
- https://github.com/jwt/ruby-jwe/security/advisories/GHSA-c7p4-hx26-pr73
- https://nvd.nist.gov/vuln/detail/CVE-2025-54887
- https://github.com/jwt/ruby-jwe/commit/1e719d79ba3d7aadaa39a2f08c25df077a0f9ff1
