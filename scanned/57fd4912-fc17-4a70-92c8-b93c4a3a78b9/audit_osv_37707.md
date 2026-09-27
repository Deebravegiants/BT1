# [M] Botan: Case-Insensitive CN Values Bypass DNS excludedSubtrees Name Constraints (RFC 5280 Violation)

## Summary
Severity: Medium
Advisory: CVE-2026-32884
Aliases: GHSA-7c3g-7763-ggj5
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-32884
Type: osv

## Details
Botan is a C++ cryptography library. Prior to version 3.11.0, during processing of an X.509 certificate path using name constraints which restrict the set of allowable DNS names, if no subject alternative name is defined in the end-entity certificate Botan would check that the CN was allowed by the DNS name constraints, even though this check is technically not required by RFC 5280. However this check failed to account for the possibility of a mixed-case CN. Thus a certificate with CN=Sub.EVIL.COM and no subject alternative name would bypasses an excludedSubtrees constraint for evil.com because the comparison is case-sensitive. This issue has been patched in version 3.11.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32884.json
- https://github.com/randombit/botan/security/advisories/GHSA-7c3g-7763-ggj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-32884
