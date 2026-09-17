# [C] SQL Injection in USOC

## Summary
Severity: Critical
Advisory: CVE-2022-21643
Aliases: GHSA-fjp4-phjh-jgmc
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-01-04
Source: https://osv.dev/vulnerability/CVE-2022-21643
Type: osv

## Details
USOC is an open source CMS with a focus on simplicity. In affected versions USOC allows for SQL injection via register.php. In particular usernames, email addresses, and passwords provided by the user were not sanitized and were used directly to construct a sql statement. Users are advised to upgrade as soon as possible. There are not workarounds for this issue.

## References
- https://github.com/Aaron-Junker/USOC/security/advisories/GHSA-fjp4-phjh-jgmc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21643.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21643
- https://github.com/Aaron-Junker/USOC/commit/21e8bfd7a9ab0b7f9344a7a3a7c32a7cdd5a0b69
