# [H] XWiki Platform has an SQL injection in getdocuments.vm with sort parameter

## Summary
Severity: High
Advisory: GHSA-wh34-m772-5398
CVE: CVE-2024-55663
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-wh34-m772-5398
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-distribution-war` — affected >=6.3-milestone-2 <13.10.5
- Maven: `org.xwiki.platform:xwiki-platform-distribution-war` — affected >=14.0-rc-1 <14.3-rc-1

## Details
### Impact

In `getdocument.vm` ; the ordering of the returned documents is defined from an unsanitized request parameter (request.sort) and can allow any user to inject HQL.

Depending on the used database backend, the attacker may be able to not only obtain confidential information such as password hashes from the database, but also execute UPDATE/INSERT/DELETE queries.

It's possible to employ database backend dependent techniques of breaking out of HQL query context, described, for example, here: https://www.sonarsource.com/blog/exploiting-hibernate-injections.

### Patches

This has been patched in 13.10.5 and 14.3-rc-1.

### Workarounds

There is no known workaround, other than upgrading XWiki.

### References

https://jira.xwiki.org/browse/XWIKI-17568

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-wh34-m772-5398
- https://nvd.nist.gov/vuln/detail/CVE-2024-55663
- https://github.com/xwiki/xwiki-platform/commit/673076e2e8b88a36cdeaf7007843aa9ca1a068a0
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-17568
