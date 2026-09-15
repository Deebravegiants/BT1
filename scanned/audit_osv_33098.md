# [M] Path-Traversal in report scheduler

## Summary
Severity: Medium
Advisory: CVE-2025-39664
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-39664
Type: osv

## Details
Insufficient escaping in the report scheduler within Checkmk <2.4.0p13, <2.3.0p38, <2.2.0p46 and 2.1.0 (EOL) allows authenticated attackers to define the storage location of report file pairs beyond their intended root directory.

## References
- http://seclists.org/fulldisclosure/2025/Oct/7
- https://checkmk.com/werk/17984
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39664.json
- https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20250730-01_Checkmk_Path_Traversal
- https://nvd.nist.gov/vuln/detail/CVE-2025-39664
