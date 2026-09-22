# [M] CVE-2025-51825

## Summary
Severity: Medium
Advisory: CVE-2025-51825
Aliases: GHSA-gj8w-ffq9-6828
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-51825
Type: osv

## Details
JeecgBoot versions from 3.4.3 up to 3.8.0 were found to contain a SQL injection vulnerability in the /jeecg-boot/online/cgreport/head/parseSql endpoint, which allows bypassing SQL blacklist restrictions.

## References
- https://r4gd0ll.github.io/2025/JEECGBOOT_BYPASS_SQLInject.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51825.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51825
- https://github.com/jeecgboot/JeecgBoot/issues/8335
