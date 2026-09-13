# [M] XWiki Platform vulnerable to page render failure due to broken translations

## Summary
Severity: Medium
Advisory: GHSA-9jq5-xwqw-q8j3
CVE: CVE-2023-29520
CWE: CWE-248, CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-9jq5-xwqw-q8j3
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-localization-source-wiki` — affected >=4.3-milestone-2 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-localization-source-wiki` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-localization-source-wiki` — affected >=14.5 <14.10.1

## Details
### Impact

It's possible to break many translations coming from wiki pages by creating a corrupted document containing a translation object.

### Patches

The vulnerability has been patched in XWiki 15.0-rc-1, 14.10.1, 14.4.8, and 13.10.11.

### Workarounds

There is no other workaround other than fixing any way to create a document that fail to load.

### References

https://jira.xwiki.org/browse/XWIKI-20460

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9jq5-xwqw-q8j3
- https://nvd.nist.gov/vuln/detail/CVE-2023-29520
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20460
