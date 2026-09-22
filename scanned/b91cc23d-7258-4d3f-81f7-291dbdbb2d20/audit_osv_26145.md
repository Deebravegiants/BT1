# [M] CVE-2023-5182

## Summary
Severity: Medium
Advisory: CVE-2023-5182
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-06
Source: https://osv.dev/vulnerability/CVE-2023-5182
Type: osv

## Details
Sensitive data could be exposed in logs of subiquity version 23.09.1 and earlier. An attacker in the adm group could use this information to find hashed passwords and possibly escalate their privilege.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5182.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5182
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-5182
- https://github.com/canonical/subiquity/pull/1820/commits/62e126896fb063808767d74d00886001e38eaa1c
- https://github.com/canonical/subiquity
