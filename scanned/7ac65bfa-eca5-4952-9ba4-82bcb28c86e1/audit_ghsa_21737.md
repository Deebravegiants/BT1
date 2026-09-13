# [M] Missing authorization in xwiki-platform

## Summary
Severity: Medium
Advisory: GHSA-gf7x-2j2x-7f73
CVE: CVE-2022-23617
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-gf7x-2j2x-7f73
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <12.10.6
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=13.0 <13.2-rc-1

## Details
### Impact

Any user with edit right can copy the content of a page it does not have access to by using it as template of a new page.

### Patches

It has been patched in XWiki 13.2CR1 and 12.10.6

### Workarounds

There is no workaround beside patching.

### References

https://jira.xwiki.org/browse/XWIKI-18430

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [our security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gf7x-2j2x-7f73
- https://nvd.nist.gov/vuln/detail/CVE-2022-23617
- https://github.com/xwiki/xwiki-platform/commit/30c52b01559b8ef5ed1035dac7c34aaf805764d5
- https://github.com/xwiki/xwiki-platform/commit/b35ef0edd4f2ff2c974cbeef6b80fcf9b5a44554
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18430
