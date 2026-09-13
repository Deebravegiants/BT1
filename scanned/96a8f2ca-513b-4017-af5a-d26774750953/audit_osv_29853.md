# [M] Logging of sitesecret to automations log

## Summary
Severity: Medium
Advisory: CVE-2024-47094
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-47094
Type: osv

## Details
Insertion of Sensitive Information into Log File in Checkmk GmbH's Checkmk versions <2.3.0p22, <2.2.0p37, <2.1.0p50 (EOL) causes remote site secrets to be written to web log files accessible to local site users.

## References
- https://checkmk.com/werk/17342
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47094.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47094
