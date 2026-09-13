# [C] Census CSWeb path traversal

## Summary
Severity: Critical
Advisory: CVE-2025-60946
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2025-60946
Type: osv

## Details
Census CSWeb 8.0.1 allows arbitrary file path input. A remote, authenticated attacker could access unintended file directories. Fixed in 8.1.0 alpha.

## References
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2026/va-26-079-01.json
- https://www.cve.org/CVERecord?id=CVE-2025-60946
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60946.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60946
- https://github.com/csprousers/csweb/commit/eba0b59a243390a1a4f9524cce6dbc0314bf0d91
- https://github.com/hx381/cspro-exploits
