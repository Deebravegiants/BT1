# [M] XWiki missing authorization when accessing the wiki level attachments list and metadata via REST API

## Summary
Severity: Medium
Advisory: GHSA-r5cr-xm48-97xp
CVE: CVE-2025-46554
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-r5cr-xm48-97xp
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=1.8.1 <14.10.22
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=15.0-rc-1 <15.10.12
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=16.0.0-rc-1 <16.4.3
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=16.5.0-rc-1 <16.7.0

## Details
### Impact

Anyone can access the metadata of any attachment in the wiki using the wiki attachment REST endpoint. It's not filtering the result depending on current user rights, a not authenticated user could exploit this even in a totally private wiki.

To reproduce:

* remove view from guest on the whole wiki
* logout
* access http://127.0.0.1:8080/xwiki/rest/wikis/xwiki/spaces/Sandbox/pages/WebHome/attachments

You get a list of attachments, while the expected result should be an empty list.

### Patches

This vulnerability has been fixed in XWiki 14.10.22, 15.10.12, 16.7.0-rc-1 and 16.4.3.

### Workarounds

We're not aware of any workaround except upgrading.

### References
* https://jira.xwiki.org/browse/XWIKI-22424
* https://jira.xwiki.org/browse/XWIKI-22427
* https://github.com/xwiki/xwiki-platform/commit/a43e933ddeda17dad1772396e1757998260e9342#diff-0

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

Issue reported by [Lukas Monert](https://github.com/LMonert).

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-r5cr-xm48-97xp
- https://nvd.nist.gov/vuln/detail/CVE-2025-46554
- https://github.com/xwiki/xwiki-platform/commit/37ecea84fdd053c33733c2ae9a0778bf98eae608
- https://github.com/xwiki/xwiki-platform/commit/a43e933ddeda17dad1772396e1757998260e9342
- https://github.com/xwiki/xwiki-platform/commit/c02ce7843a39851865b9d7b6132e32fdd21e3856
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22424
- https://jira.xwiki.org/browse/XWIKI-22427
