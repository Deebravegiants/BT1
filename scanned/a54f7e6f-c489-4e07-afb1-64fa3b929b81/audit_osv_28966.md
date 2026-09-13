# [H] Suricata http2: oom from duplicate headers

## Summary
Severity: High
Advisory: CVE-2024-38535
Aliases: GHSA-cg8j-7mwm-v563
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-11
Source: https://osv.dev/vulnerability/CVE-2024-38535
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Suricata can run out of memory when parsing crafted HTTP/2 traffic. Upgrade to 6.0.20 or 7.0.6.

## References
- https://redmine.openinfosecfoundation.org/issues/7104
- https://redmine.openinfosecfoundation.org/issues/7105
- https://redmine.openinfosecfoundation.org/issues/7112
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38535.json
- https://github.com/OISF/suricata/security/advisories/GHSA-cg8j-7mwm-v563
- https://nvd.nist.gov/vuln/detail/CVE-2024-38535
- https://github.com/OISF/suricata/commit/62d5cac1b8483d5f9d2b79833a4e59f5d80129b7
- https://github.com/OISF/suricata/commit/c82fa5ca0d1ce0bd8f936e0b860707a6571373b2
