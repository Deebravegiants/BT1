# [C] XWiki Platform vulnerable to privilege escalation via async macro and IconThemeSheet from the user profile

## Summary
Severity: Critical
Advisory: GHSA-vwr6-qp4q-2wj7
CVE: CVE-2023-26472
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-vwr6-qp4q-2wj7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-icon-ui` — affected >=6.2-milestone-1 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-icon-ui` — affected >=14.0 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-icon-ui` — affected >=14.5 <14.9

## Details
### Impact

One can execute any wiki content with the right of IconThemeSheet author by creating an icon theme with the following content:

```
}}}
{{async async="true"}}
{{groovy}}
  println("Hello from Groovy!")
{{/groovy}}
{{/async}}
{{{
```

Can be done by creating a new page or even through the user profile for users not having edit right.

### Patches

This has been patched in XWiki 14.9, 14.4.6, and 13.10.10.

### Workarounds

An easy workaround is to actually fix the bug in the page `IconThemesCode.IconThemeSheet` by applying the following modification: https://github.com/xwiki/xwiki-platform/commit/48caf7491595238af2b531026a614221d5d61f38#diff-2ec9d716673ee049937219cdb0a92e520f81da14ea84d144504b97ab2bdae243R45

### References

https://jira.xwiki.org/browse/XWIKI-19731

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](http://jira.xwiki.org)
* Email us at [Security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-vwr6-qp4q-2wj7
- https://nvd.nist.gov/vuln/detail/CVE-2023-26472
- https://github.com/xwiki/xwiki-platform/commit/48caf7491595238af2b531026a614221d5d61f38#diff-2ec9d716673ee049937219cdb0a92e520f81da14ea84d144504b97ab2bdae243R45
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19731
