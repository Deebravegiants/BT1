# [H] Apache CloudStack: LDAP provider configuration disclosure

## Summary
Severity: High
Advisory: CVE-2026-59780
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-59780
Type: osv

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache CloudStack's LDAP authentication plugin while listing LDAP providers.











LDAP configurations can be listed by any authenticated user with access to the listLdapConfigurations API. By default, this API is available to all default roles.

















This issue affects Apache CloudStack: from 4.2.0.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.

Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59780.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-59780
