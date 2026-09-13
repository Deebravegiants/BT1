# [H] Script injection without script or programming rights through Gadget titles

## Summary
Severity: High
Advisory: GHSA-h353-hc43-95vc
CVE: CVE-2021-32621
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-h353-hc43-95vc
Type: github-advisory

## Affected
- Maven: `org.xwiki.commons:xwiki-commons-core` — affected >=0 <12.6.7
- Maven: `org.xwiki.commons:xwiki-commons-core` — affected >=12.10.0 <12.10.3

## Details
### Impact
A user without Script or Programming right is able to execute script requiring privileges by editing gadget titles in the dashboard.

### Patches
The issue has been patched in XWiki 12.6.7, 12.10.3 and 13.0RC1.

### Workarounds
There's no easy workaround for this issue, it is recommended to upgrade XWiki.

### References
https://jira.xwiki.org/browse/XWIKI-17794

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [JIRA](https://jira.xwiki.org)
* Email us at [XWiki security mailing-list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h353-hc43-95vc
- https://nvd.nist.gov/vuln/detail/CVE-2021-32621
- https://github.com/xwiki/xwiki-platform/commit/bb7068bd911f91e5511f3cfb03276c7ac81100bc
- https://github.com/xwiki/xwiki-platform
- https://jay-from-future.github.io/cve/2021/06/17/xwiki-rce-cve.html
- https://jira.xwiki.org/browse/XWIKI-17794
