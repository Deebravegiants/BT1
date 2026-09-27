# [C] omd: Local privilege escalation when executing omd commands as root

## Summary
Severity: Critical
Advisory: CVE-2025-39666
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2025-39666
Type: osv

## Details
Local privilege escalation in Checkmk 2.2.0 (EOL), Checkmk 2.3.0 before 2.3.0p46, Checkmk 2.4.0 before 2.4.0p25, and Checkmk 2.5.0 (beta) before 2.5.0b3 allows a site user to escalate their privileges to root, by manipulating files in the site context that are processed when the `omd` administrative command is run by root.

## References
- https://checkmk.com/werk/18891
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39666.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39666
