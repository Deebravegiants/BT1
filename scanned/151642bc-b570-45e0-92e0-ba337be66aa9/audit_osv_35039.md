# [H] CVE-2025-67896

## Summary
Severity: High
Advisory: CVE-2025-67896
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2025-12-14
Source: https://osv.dev/vulnerability/CVE-2025-67896
Type: osv

## Details
Exim before 4.99.1, with certain non-default rate-limit configurations, allows a remote heap-based buffer overflow because database records are cast directly to internal structures without validation.

## References
- http://www.openwall.com/lists/oss-security/2025/12/14/1
- http://www.openwall.com/lists/oss-security/2025/12/18/3
- https://exim.org/static/doc/security/
- https://exim.org/static/doc/security/EXIM-Security-2025-12-09.1/report.txt
- https://www.openwall.com/lists/oss-security/2025/12/11/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67896.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67896
