# [H] org.xwiki.platform:xwiki-platform-oldcore allows SQL injection in short form select requests through the script query API

## Summary
Severity: High
Advisory: GHSA-g9jj-75mx-wjcx
CVE: CVE-2025-32968
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-23
Source: https://github.com/advisories/GHSA-g9jj-75mx-wjcx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.6-milestone-1 <15.10.16
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=16.0.0-rc-1 <16.4.6
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=16.5.0-rc-1 <16.10.1

## Details
### Impact

It is possible for a user with SCRIPT right to escape from the HQL execution context and perform a blind SQL injection to execute arbitrary SQL statements on the database backend.

Depending on the used database backend, the attacker may be able to not only obtain confidential information such as password hashes from the database, but also execute UPDATE/INSERT/DELETE queries.

The vulnerability may be tested in a default installation of XWIki Standard Flavor, including using the official Docker containers.

For example, with a MySQL or MariaDB database, you can use the following script (which a user having SCRIPT right but not PROGRAMMING right) to get the content of the xwikistrings table (which contain all the short string fields stored in objects, including passwords):

```
{{velocity}}
$services.query.hql("where 1<>'1\'' union select concat(XWS_NAME, XWS_VALUE) from xwikistrings #'").execute()
{{/velocity}}
```

### Patches

This has been patched in 16.10.1, 16.4.6 and 15.10.16.

### Workarounds

There is no known workaround, other than upgrading XWiki.

The protection added to this REST API is the same as the one used to validate complete select queries, making it more consistent. However, while the script API always had this protection for complete queries, it's important to note that it's a very strict protection and some valid, but complex, queries might suddenly require the author to have programming right.

### References

https://jira.xwiki.org/browse/XWIKI-22718

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-g9jj-75mx-wjcx
- https://nvd.nist.gov/vuln/detail/CVE-2025-32968
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22718
