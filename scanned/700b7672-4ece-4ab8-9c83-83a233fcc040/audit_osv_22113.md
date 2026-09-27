# [C] SQL Injection via search in USOC

## Summary
Severity: Critical
Advisory: CVE-2022-21644
Aliases: GHSA-89jg-6fr3-9q4h
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-01-04
Source: https://osv.dev/vulnerability/CVE-2022-21644
Type: osv

## Details
USOC is an open source CMS with a focus on simplicity. In affected versions USOC allows for SQL injection via usersearch.php. In search terms provided by the user were not sanitized and were used directly to construct a sql statement. The only users permitted to search are site admins. Users are advised to upgrade as soon as possible. There are not workarounds for this issue.

## References
- https://github.com/Aaron-Junker/USOC/security/advisories/GHSA-89jg-6fr3-9q4h
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21644.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21644
- https://github.com/Aaron-Junker/USOC/commit/06217c66c8f9b114726b21633eabcd88ac9034aa
