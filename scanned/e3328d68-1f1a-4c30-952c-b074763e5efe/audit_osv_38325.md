# [H] CVE-2026-38950

## Summary
Severity: High
Advisory: CVE-2026-38950
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-38950
Type: osv

## Details
An issue in ESA AnomalyMatch before 1.3.1 allow attackers to execute arbitrary code via crafted model checkpoint files. The affected components load model files from session directories using torch.load() with unrestricted deserialization.

## References
- https://github.com/Accenture/AARO-Bugs/blob/master/AARO-CVE-List.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38950.json
- https://imlabs.info/research/security_advisory_esa_anomaly_match_unsafe_deserialization_cve_2026_38950_ivan_markovic_052026.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-38950
- https://github.com/esa/AnomalyMatch/pull/9
