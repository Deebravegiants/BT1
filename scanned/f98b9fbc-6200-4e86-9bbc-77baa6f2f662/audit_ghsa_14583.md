# [M] XWiki Platform subject to Uncontrolled Resource Consumption

## Summary
Severity: Medium
Advisory: GHSA-92wp-r7hm-42g7
CVE: CVE-2023-26470
CWE: CWE-400, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-92wp-r7hm-42g7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <14.0-rc-1

## Details
### Impact

It's possible to make the farm unusable by adding an object to a page with a huge number (e.g. 67108863). This will most of the time fill the memory allocated to XWiki and make it unusable every time this document is manipulated.

### Patches
It has been patched in XWiki 14.0

### Workarounds
There is no workaround.

### References
https://jira.xwiki.org/browse/XWIKI-19223

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [our security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-92wp-r7hm-42g7
- https://nvd.nist.gov/vuln/detail/CVE-2023-26470
- https://github.com/xwiki/xwiki-platform/commit/04e5a89d2879b160cdfaea846024d3d9c1a525e6
- https://github.com/xwiki/xwiki-platform/commit/db3d1c62fc5fb59fefcda3b86065d2d362f55164
- https://github.com/xwiki/xwiki-platform/commit/fdfce062642b0ac062da5cda033d25482f4600fa
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19223
