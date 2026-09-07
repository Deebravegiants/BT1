# [C] NetBird VPN does not remove the default password of an admin account

## Summary
Severity: Critical
Advisory: GHSA-g3j4-58mp-3x25
CVE: CVE-2025-10678
CWE: CWE-1392
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-20
Source: https://github.com/advisories/GHSA-g3j4-58mp-3x25
Type: github-advisory

## Affected
- Go: `github.com/netbirdio/netbird` — affected >=0 <0.57.0

## Details
NetBird VPN when installed using vendor's provided script failed to remove or change default password of an admin account created by ZITADEL.
This issue affects instances installed using vendor's provided script. This issue may affect instances created with Docker if the default password was not changed nor the user was removed.

This issue has been fixed in version 0.57.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10678
- https://github.com/netbirdio/netbird/commit/cf7f6c355f713e83cf171b79e08dac60b316e4fd
- https://cert.pl/en/posts/2025/10/CVE-2025-10678
- https://github.com/netbirdio/netbird
- https://netbird.io
