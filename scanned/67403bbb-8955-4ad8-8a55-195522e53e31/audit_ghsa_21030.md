# [H] XWiki Platform Web Parent POM vulnerable to XSS in the attachment history

## Summary
Severity: High
Advisory: GHSA-mxf2-4r22-5hq9
CVE: CVE-2022-36094
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-mxf2-4r22-5hq9
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=1.0 <13.10.6
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=14.0 <14.3-rc-1

## Details
### Impact

It's possible to store a JavaScript which will be executed by anyone viewing the history of an attachment containing javascript in its name.

For example, attachment a file with name `><img src=1 onerror=alert(1)>.jpg` will execute the alert.

### Patches

This issue has been patched in XWiki 13.10.6 and 14.3RC1.

### Workarounds

It is possible to replace viewattachrev.vm, the entry point for this attack, by a [patch](https://github.com/xwiki/xwiki-platform/commit/047ce9fa4a7c13f3883438aaf54fc50f287a7e8e)ed version from the patch without updating XWiki.

### References

* https://jira.xwiki.org/browse/XWIKI-19612

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-mxf2-4r22-5hq9
- https://nvd.nist.gov/vuln/detail/CVE-2022-36094
- https://github.com/xwiki/xwiki-platform/commit/047ce9fa4a7c13f3883438aaf54fc50f287a7e8e
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19612
