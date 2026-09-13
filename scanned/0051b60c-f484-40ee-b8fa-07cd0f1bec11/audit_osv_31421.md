# [M] LDAP credentials logged to Apache error log

## Summary
Severity: Medium
Advisory: CVE-2025-1075
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2025-1075
Type: osv

## Details
Insertion of Sensitive Information into Log File in Checkmk GmbH's Checkmk versions <2.3.0p27, <2.2.0p40, and 2.1.0p51 (EOL) causes LDAP credentials to be written to Apache error log file accessible to administrators.

## References
- https://checkmk.com/werk/17495
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1075.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1075
