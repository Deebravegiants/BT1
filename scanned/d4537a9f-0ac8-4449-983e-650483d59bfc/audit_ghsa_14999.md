# [C] XWiki programming rights may be inherited by inclusion

## Summary
Severity: Critical
Advisory: GHSA-qcj3-wpgm-qpxh
CVE: CVE-2024-38369
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-24
Source: https://github.com/advisories/GHSA-qcj3-wpgm-qpxh
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-include` — affected >=0 <15.0-rc-1

## Details
### Impact

The content of a document included using `{{include reference="targetdocument"/}}` is executed with the right of the includer and not with the right of its author.

This means that any user able to modify the target document can impersonate the author of the content which used the `include` macro.

### Patches

This has been patched in XWiki 15.0 RC1 by making the default behavior safe.

### Workarounds

Make sure to protect any included document to make sure only allowed users can modify it.

A workaround have been provided in 14.10.2 to allow forcing to execute the included content with the target content author instead of the default behavior. See https://extensions.xwiki.org/xwiki/bin/view/Extension/Include%20Macro#HAuthor for more details.

### References

https://jira.xwiki.org/browse/XWIKI-5027
https://jira.xwiki.org/browse/XWIKI-20471

### For more information
If you have any questions or comments about this advisory:
*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-qcj3-wpgm-qpxh
- https://nvd.nist.gov/vuln/detail/CVE-2024-38369
- https://github.com/xwiki/xwiki-platform/commit/0a4f9b026ba9931516b4e9b3019da8da838c7ac6
- https://github.com/xwiki/xwiki-platform/commit/b48116a3ebe9ce928c401b5d068d4db7e7239575
- https://github.com/xwiki/xwiki-platform/commit/c1fb14402ce2ee569c5a8e3f1f8e64ae45dfbfb0
- https://github.com/xwiki/xwiki-platform/commit/d1a84a3eea38305ff8e10ba411910c0675ac157c
- https://github.com/xwiki/xwiki-platform/commit/f627abe2dc39b07ff75fe68398cc8a1bbc743ef7
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20471
- https://jira.xwiki.org/browse/XWIKI-5027
