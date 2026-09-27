# [C] Privilege Escalation in Windows License plugin for Checkmk Windows Agent

## Summary
Severity: Critical
Advisory: CVE-2025-32919
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-32919
Type: osv

## Details
Use of an insecure temporary directory in the Windows License plugin for the Checkmk Windows Agent allows Privilege Escalation. This issue affects Checkmk: from 2.4.0 before 2.4.0p13, from 2.3.0 before 2.3.0p38, from 2.2.0 before 2.2.0p46, and all versions of 2.1.0 (EOL).

## References
- http://seclists.org/fulldisclosure/2025/Oct/6
- https://checkmk.com/werk/18207
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32919.json
- https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20250724-01_Checkmk_Agent_Privilege_Escalation_via_Insecure_Temporary_Files
- https://nvd.nist.gov/vuln/detail/CVE-2025-32919
