# [M] Botan has an Authorization Error due to Name Constraint Decoding Bug

## Summary
Severity: Medium
Advisory: CVE-2024-39312
Aliases: GHSA-jp24-56jm-gg86
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/CVE-2024-39312
Type: osv

## Details
Botan is a C++ cryptography library. X.509 certificates can identify elliptic curves using either an object identifier or using explicit encoding of the parameters. A bug in the parsing of name constraint extensions in X.509 certificates meant that if the extension included both permitted subtrees and excluded subtrees, only the permitted subtree would be checked. If a certificate included a name which was permitted by the permitted subtree but also excluded by excluded subtree, it would be accepted. Fixed in versions 3.5.0 and 2.19.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39312.json
- https://github.com/randombit/botan/security/advisories/GHSA-jp24-56jm-gg86
- https://nvd.nist.gov/vuln/detail/CVE-2024-39312
