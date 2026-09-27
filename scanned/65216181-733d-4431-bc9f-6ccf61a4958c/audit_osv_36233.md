# [C] OpenMetadata Server-Side Template Injection (SSTI) in FreeMarker email templates that leads to RCE

## Summary
Severity: Critical
Advisory: CVE-2026-22244
Aliases: GHSA-5f29-2333-h9c7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-22244
Type: osv

## Details
OpenMetadata is a unified metadata platform. Versions 1.5.0 through 1.11.3 are vulnerable to remote code execution via Server-Side Template Injection (SSTI) in FreeMarker email templates. An attacker must have administrative privileges to exploit the vulnerability. Version 1.11.4 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22244.json
- https://github.com/open-metadata/OpenMetadata/security/advisories/GHSA-5f29-2333-h9c7
- https://nvd.nist.gov/vuln/detail/CVE-2026-22244
- https://github.com/open-metadata/OpenMetadata/commit/bffe7c45807763f9b682021d4211c478d2a08bb3
- https://github.com/open-metadata/OpenMetadata/commit/d17d13cee87db139e5d8f778547174f8ee341108
