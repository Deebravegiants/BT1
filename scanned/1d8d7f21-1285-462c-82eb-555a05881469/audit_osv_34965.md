# [C] CVE-2025-66913

## Summary
Severity: Critical
Advisory: CVE-2025-66913
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2025-66913
Type: osv

## Details
JimuReport thru version 2.1.3 is vulnerable to remote code execution when processing user-controlled H2 JDBC URLs. The application passes the attacker-supplied JDBC URL directly to the H2 driver, allowing the use of certain directives to execute arbitrary Java code. A different vulnerability than CVE-2025-10770.

## References
- https://gist.github.com/Catherines77/f15d53e9705b24cf018e5bffed3e8234
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66913.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66913
- https://github.com/jeecgboot/jimureport/issues/4306
