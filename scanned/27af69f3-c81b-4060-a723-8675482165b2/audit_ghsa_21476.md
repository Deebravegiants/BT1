# [H] Creation of new database tables through login form on PostgreSQL

## Summary
Severity: High
Advisory: GHSA-4x5r-6v26-7j4v
CVE: CVE-2022-41932
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-4x5r-6v26-7j4v
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <13.10.8
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.0.0 <14.4.2
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.5.0 <14.6-rc-1

## Details
### Impact

It's possible to make XWiki create many new schemas and fill them with tables just by using a crafted user identifier in the login form.

### Patches

The problem has been patched in XWiki 13.10.8, 14.6RC1 and 14.4.2.

### Workarounds

The only workarounds for this are:
* use an authenticator which does interpret the login as a reference to a document
* using a different database than PostgreSQL
* upgrade XWiki

### References

https://jira.xwiki.org/browse/XWIKI-19886

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-4x5r-6v26-7j4v
- https://nvd.nist.gov/vuln/detail/CVE-2022-41932
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19886
