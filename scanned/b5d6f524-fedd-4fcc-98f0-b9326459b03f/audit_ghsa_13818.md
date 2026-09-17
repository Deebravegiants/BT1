# [H] Cross-Site Request Forgery with QueryOnXWiki allows arbitrary database queries

## Summary
Severity: High
Advisory: GHSA-4f4c-rhjv-4wgv
CVE: CVE-2023-48293
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-20
Source: https://github.com/advisories/GHSA-4f4c-rhjv-4wgv
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib:xwiki-application-admintools` — affected >=0 <4.5.1

## Details
### Impact
A CSRF vulnerability in the query on XWiki tool allows executing arbitrary database queries on the database of the XWiki installation. Among other things, this allows modifying and deleting all data of the wiki. This could be both used to damage the wiki and to create an account with elevated privileges for the attacker, thus impacting the confidentiality, integrity and availability of the whole XWiki instance. A possible attack vector are comments on the wiki, by embedding an image with wiki syntax like `[[image:path:/xwiki/bin/view/Admin/QueryOnXWiki?query=DELETE%20FROM%20xwikidoc]]`, all documents would be deleted from the database when an admin user views this comment.

### Patches
This has been patched in Admin Tools Application 4.5.1 by adding form token checks.

### Workarounds
The [patch](https://github.com/xwiki-contrib/application-admintools/commit/45298b4fbcafba6914537dcdd798a1e1385f9e46) can also be applied manually to the affected pages. Alternatively, if the query tool is not needed, by deleting the document `Admin.SQLToolsGroovy`, all database query tools can be deactivated.

### References

* https://jira.xwiki.org/browse/ADMINTOOL-92
* https://github.com/xwiki-contrib/application-admintools/commit/45298b4fbcafba6914537dcdd798a1e1385f9e46

## References
- https://github.com/xwiki-contrib/application-admintools/security/advisories/GHSA-4f4c-rhjv-4wgv
- https://nvd.nist.gov/vuln/detail/CVE-2023-48293
- https://github.com/xwiki-contrib/application-admintools/commit/45298b4fbcafba6914537dcdd798a1e1385f9e46
- https://github.com/xwiki-contrib/application-admintools
- https://jira.xwiki.org/browse/ADMINTOOL-92
