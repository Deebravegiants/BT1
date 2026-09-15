# [H] Suricata http1: infinite recursion in decompression

## Summary
Severity: High
Advisory: CVE-2026-22260
Aliases: GHSA-3gm8-84cm-5x22
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-22260
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. Starting in version 8.0.0 and prior to version 8.0.3, Suricata can crash with a stack overflow. Version 8.0.3 patches the issue. As a workaround, use default values for `request-body-limit` and `response-body-limit`.

## References
- https://redmine.openinfosecfoundation.org/issues/8185
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22260.json
- https://github.com/OISF/suricata/security/advisories/GHSA-3gm8-84cm-5x22
- https://nvd.nist.gov/vuln/detail/CVE-2026-22260
- https://github.com/OISF/suricata/commit/0dddac7278c8b9cf3c1e4c1c71e620a78ec1c185
