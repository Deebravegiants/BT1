# [M] XWiki Platform's tags on non-viewable pages can be revealed to users

## Summary
Severity: Medium
Advisory: GHSA-7f2f-pcv3-j2r7
CVE: CVE-2023-34466
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-7f2f-pcv3-j2r7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-tag-api` — affected >=5.0-milestone-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-tag-api` — affected >=14.5 <14.10.4

## Details
### Impact
Tags from pages not viewable to the current user are leaked by the tags API. 
This information can also be exploited to infer the document reference of non-viewable pages.

### Patches
This vulnerability has been patched in XWiki 14.4.8, 14.10.4, and 15.0 RC1.

### Workarounds
There is no workaround apart from upgrading to a fixed version.

### References
- https://jira.xwiki.org/browse/XWIKI-20002

### For more information

If you have any questions or comments about this advisory:

*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-7f2f-pcv3-j2r7
- https://nvd.nist.gov/vuln/detail/CVE-2023-34466
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20002
