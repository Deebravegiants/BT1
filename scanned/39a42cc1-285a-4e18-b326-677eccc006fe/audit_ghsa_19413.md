# [H] The XWiki JIRA extension allows data leak through an XXE attack by using a fake JIRA server

## Summary
Severity: High
Advisory: GHSA-wc53-4255-gw3f
CVE: CVE-2025-31487
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-wc53-4255-gw3f
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.jira:jira-macro-default` — affected >=4.2 <8.5.6

## Details
### Impact
If the JIRA macro is installed, any logged in XWiki user could edit his/her user profile wiki page and use that JIRA macro, specifying a fake JIRA URL that returns an XML specifying a DOCTYPE pointing to a local file on the XWiki server host and displaying that file's content in one of the returned JIRA fields (such as the summary or description for example).

For example:

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<rss version="0.92">
...
    <item>
      <title>&xxe;</title>
      <link>https://jira.xwiki.org/browse/XE-307</link>
      <project id="10222" key="XE">{RETIRED} XWiki Enterprise</project>
      <description>&xxe;</description>
      <environment/>
...
```

### Patches
The vulnerability has been patched in the JIRA Extension v8.6.5.

### Workarounds
No easy workaround except to upgrade (which is easy using the XWiki Extension Manager).

### References
* https://github.com/xwiki-contrib/jira/commit/98a74c2a516b42689c73b13ecd94e9c1998fa9cb and https://github.com/xwiki-contrib/jira/commit/5049e352d16f8356734de70daf1202301f170ee6
* https://jira.xwiki.org/browse/JIRA-49

### For more information
If you have any questions or comments about this advisory:
*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki-contrib/jira/security/advisories/GHSA-wc53-4255-gw3f
- https://nvd.nist.gov/vuln/detail/CVE-2025-31487
- https://github.com/xwiki-contrib/jira/commit/5049e352d16f8356734de70daf1202301f170ee6
- https://github.com/xwiki-contrib/jira/commit/98a74c2a516b42689c73b13ecd94e9c1998fa9cb
- https://github.com/xwiki-contrib/jira
- https://jira.xwiki.org/browse/JIRA-49
