# [M] Suricata detect/transform: use-after-free in dotprefix transform

## Summary
Severity: Medium
Advisory: CVE-2026-45751
Aliases: GHSA-59q6-j4w8-8pjx
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45751
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5, Suricata's inspection-buffer helper could leave an inspection pointer referencing freed memory after a chained transform caused the backing buffer to be reallocated. The issue is reached during a specific network traffic processing, and requires a specific but not malicious rule. Versions 7.0.16 and 8.0.5 contain a fix. As a workaround, avoid rules that chain `dotprefix` transform after another one.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8537
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45751.json
- https://github.com/OISF/suricata/security/advisories/GHSA-59q6-j4w8-8pjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45751
