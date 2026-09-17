# [M] ALPINE-CVE-2026-32884

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-32884
Ecosystem: Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32884
Type: osv

## Affected
- Alpine:v3.24: `botan3` — affected >=0 <3.11.0-r0

## Details
Botan is a C++ cryptography library. Prior to version 3.11.0, during processing of an X.509 certificate path using name constraints which restrict the set of allowable DNS names, if no subject alternative name is defined in the end-entity certificate Botan would check that the CN was allowed by the DNS name constraints, even though this check is technically not required by RFC 5280. However this check failed to account for the possibility of a mixed-case CN. Thus a certificate with CN=Sub.EVIL.COM and no subject alternative name would bypasses an excludedSubtrees constraint for evil.com because the comparison is case-sensitive. This issue has been patched in version 3.11.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32884
