# [C] XWiki Platform vulnerable to stored cross-site scripting in ClassEditSheet page via name parameters

## Summary
Severity: Critical
Advisory: GHSA-4wc6-hqv9-qc97
CVE: CVE-2023-35153
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-4wc6-hqv9-qc97
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=5.4.4 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=14.5 <14.10.4
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=15.0-rc-1 <15.0

## Details
### Impact
A stored XSS can be exploited by users with edit rights by adding a `AppWithinMinutes.FormFieldCategoryClass` class on a page and setting the payload on the page title.
Then, any user visiting `/xwiki/bin/view/AppWithinMinutes/ClassEditSheet` executes the payload.

See https://jira.xwiki.org/browse/XWIKI-20365 for me details.

### Patches
The issue has been patched on XWiki 14.4.8, 14.10.4, and 15.0 ?

### Workarounds
The issue can be fixed by updating `AppWithinMinutes.ClassEditSheet` with this [patch](https://github.com/xwiki/xwiki-platform/commit/1b87fec1e5b5ec00b7a8c3c3f94f6c5e22547392#diff-79e725ec7125cced7d302e1a1f955a76745af26ef28a148981b810e85335d302).

### References
- https://github.com/xwiki/xwiki-platform/commit/1b87fec1e5b5ec00b7a8c3c3f94f6c5e22547392#diff-79e725ec7125cced7d302e1a1f955a76745af26ef28a148981b810e85335d302
- https://jira.xwiki.org/browse/XWIKI-20365

### For more information

If you have any questions or comments about this advisory:

*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been reported on Intigriti by René de Sain @renniepak.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-4wc6-hqv9-qc97
- https://nvd.nist.gov/vuln/detail/CVE-2023-35153
- https://github.com/xwiki/xwiki-platform/commit/1b87fec1e5b5ec00b7a8c3c3f94f6c5e22547392#diff-79e725ec7125cced7d302e1a1f955a76745af26ef28a148981b810e85335d302
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20365
