# [C] xwiki-platform vulnerable to Remote Code Execution in Annotations

## Summary
Severity: Critical
Advisory: GHSA-h6f5-8jj5-cxhr
CVE: CVE-2023-26475
CWE: CWE-269, CWE-270
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-02
Source: https://github.com/advisories/GHSA-h6f5-8jj5-cxhr
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-annotation-ui` — affected >=2.3-milestone-1 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-annotation-ui` — affected >=14.0-rc-1 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-annotation-ui` — affected >=14.5 <14.10

## Details
### Impact

The annotation displayer does not execute the content in a restricted context. This allows executing anything with the right of the author of any document by annotating the document.

To reproduce: add an annotation with the content `{{groovy}}print "hello"{{/groovy}}` and click the yellow scare to get a display of the annotation inline.

The result is "hello" but it should be an error suggesting that it's not allowed to use the groovy macro.

### Patches
This has been patched in XWiki 13.10.11, 14.4.7 and 14.10.

### Workarounds
There is no easy workaround except to upgrade.

### References
https://jira.xwiki.org/browse/XWIKI-20360

https://jira.xwiki.org/browse/XWIKI-20384

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been reported by René de Sain @renniepak.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h6f5-8jj5-cxhr
- https://nvd.nist.gov/vuln/detail/CVE-2023-26475
- https://github.com/xwiki/xwiki-platform/commit/d87d7bfd8db18c20d3264f98c6deefeae93b99f7
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20360
- https://jira.xwiki.org/browse/XWIKI-20384
