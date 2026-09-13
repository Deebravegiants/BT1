# [M] CVE-2026-24231

## Summary
Severity: Medium
Advisory: CVE-2026-24231
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-24231
Type: osv

## Details
NVIDIA NemoClaw contains a vulnerability in the validateEndpointUrl() SSRF protection component, where an attacker could cause a server-side request forgery by supplying a crafted endpoint URL referencing the 0.0.0.0/8 address range through a blueprint configuration file or CLI flag. A successful exploit of this vulnerability may lead to information disclosure.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5837
- https://www.cve.org/CVERecord?id=CVE-2026-24231
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24231.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24231
