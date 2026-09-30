# [C] SQL injection vulnerability due to the keyword blacklist for defending against SQL injection will be bypassed

## Summary
Severity: Critical
Advisory: CVE-2023-28437
Aliases: GHSA-7j7j-9rw6-3r56
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-24
Source: https://osv.dev/vulnerability/CVE-2023-28437
Type: osv

## Details
Dataease is an open source data visualization and analysis tool. The blacklist for SQL injection protection is missing entries. This vulnerability has been fixed in version 1.18.5. There are no known workarounds.

## References
- https://github.com/dataease/dataease/releases/tag/v1.18.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28437.json
- https://github.com/dataease/dataease/security/advisories/GHSA-7j7j-9rw6-3r56
- https://nvd.nist.gov/vuln/detail/CVE-2023-28437
- https://github.com/dataease/dataease/issues/4795
