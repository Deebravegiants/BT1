# [H] Whole content of all documents of all wikis exposed to anybody with view right on Solr suggest service

## Summary
Severity: High
Advisory: GHSA-7fqr-97j7-jgf4
CVE: CVE-2023-48241
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-20
Source: https://github.com/advisories/GHSA-7fqr-97j7-jgf4
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-search-solr-query` — affected >=6.3-milestone-2 <14.10.15
- Maven: `org.xwiki.platform:xwiki-platform-search-solr-query` — affected >=15.0-rc-1 <15.5.1

## Details
### Impact
The Solr-based search suggestion provider that also duplicates as generic JavaScript API for search results in XWiki exposes the content of all documents of all wikis to anybody who has access to it, by default it is public. This exposes all information stored in the wiki (but not some protected information like password hashes). While there is a right check normally, the right check can be circumvented by explicitly requesting fields from Solr that don't include the data for the right check. This can be reproduced by opening `<xwiki-server>/xwiki/bin/get/XWiki/SuggestSolrService?outputSyntax=plain&media=json&nb=1000&query=q%3D*%3A*%0Aq.op%3DAND%0Afq%3Dtype%3ADOCUMENT%0Afl%3Dtitle_%2C+reference%2C+links%2C+doccontentraw_%2C+objcontent__&input=+` where `<xwiki-server>` is the URL of the XWiki installation. If this displays any results, the wiki is vulnerable.

### Patches
This has been fixed in XWiki 15.6RC1, 15.5.1 and 14.10.15 by not listing documents whose rights cannot be checked.

### Workarounds
We're not aware of a workaround apart from upgrading to a fixed version.

### References
* https://jira.xwiki.org/browse/XWIKI-21138
* https://github.com/xwiki/xwiki-platform/commit/93b8ec702d7075f0f5794bb05dfb651382596764

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-7fqr-97j7-jgf4
- https://nvd.nist.gov/vuln/detail/CVE-2023-48241
- https://github.com/xwiki/xwiki-platform/commit/93b8ec702d7075f0f5794bb05dfb651382596764
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21138
