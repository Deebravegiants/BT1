# [H] CVE-2026-9158

## Summary
Severity: High
Advisory: CVE-2026-9158
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N/E:U/S:P/RE:L/U:Green)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-9158
Type: osv

## Details
In Eclipse 4diac FORTE versions 3.0.0 to 3.1.0, a specially crafted DELETE connection command to the management interface can lead to a dangling pointer. This allows subsequent commands to access freed memory (use-after-free).

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/109
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9158.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9158
- https://github.com/eclipse-4diac/4diac-forte
