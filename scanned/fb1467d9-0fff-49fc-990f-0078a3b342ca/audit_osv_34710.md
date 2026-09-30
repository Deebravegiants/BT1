# [C] Manager-io/Manager: Complete Bypass of SSRF Protection via Time-of-Check Time-of-Use (TOCTOU)

## Summary
Severity: Critical
Advisory: CVE-2025-64180
Aliases: GHSA-j2xj-xhph-p74j
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-64180
Type: osv

## Details
Manager-io/Manager is accounting software. In Manager Desktop and Server versions 25.11.1.3085 and below, a critical vulnerability permits unauthorized access to internal network resources. The flaw lies in the fundamental design of the DNS validation mechanism. A Time-of-Check Time-of-Use (TOCTOU) condition that allows attackers to bypass network isolation and access internal services, cloud metadata endpoints, and protected network segments. The Desktop edition requires no authentication; the Server edition requires only standard authentication. This issue is fixed in version 25.11.1.3086.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64180.json
- https://github.com/Manager-io/Manager/security/advisories/GHSA-j2xj-xhph-p74j
- https://nvd.nist.gov/vuln/detail/CVE-2025-64180
