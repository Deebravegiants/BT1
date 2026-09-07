# [H] org.xwiki.platform:xwiki-platform-attachment-ui vulnerable to Code Injection

## Summary
Severity: High
Advisory: GHSA-3hjg-cghv-22ww
CVE: CVE-2023-29519
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-3hjg-cghv-22ww
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-attachment-ui` — affected >=3.0-rc-1 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-attachment-ui` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-attachment-ui` — affected >=14.5 <14.10.2

## Details
### Impact
A registered user can perform remote code execution leading to privilege escalation by injecting the proper code in the "property" field of an attachment selector, as a gadget of their own dashboard. Note that the vulnerability does not impact comments of a wiki.

### Patches
The vulnerability has been patched in XWiki 13.10.11, 14.4.8, 14.10.2, 15.0-rc-1.

### Workarounds
The problem can be worked around by applying following changes directly in XWiki.AttachmentSelector page: https://github.com/xwiki/xwiki-platform/commit/5e8725b4272cd3e5be09d3ca84273be2da6869c1.

### References

* https://jira.xwiki.org/browse/XWIKI-20364
* https://github.com/xwiki/xwiki-platform/commit/5e8725b4272cd3e5be09d3ca84273be2da6869c1

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-3hjg-cghv-22ww
- https://nvd.nist.gov/vuln/detail/CVE-2023-29519
- https://github.com/xwiki/xwiki-platform/commit/5e8725b4272cd3e5be09d3ca84273be2da6869c1
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20364
