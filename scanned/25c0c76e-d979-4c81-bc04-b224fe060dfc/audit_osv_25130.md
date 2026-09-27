# [H] Privilege escalation in agent via LD_LIBRARY_PATH

## Summary
Severity: High
Advisory: CVE-2023-31210
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-31210
Type: osv

## Details
Usage of user controlled LD_LIBRARY_PATH in agent in Checkmk 2.2.0p10 up to 2.2.0p16 allows malicious Checkmk site user to escalate rights via injection of malicious libraries

## References
- https://checkmk.com/werk/16226
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31210.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31210
