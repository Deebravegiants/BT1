# [M] Obfuscated email addresses should not be sorted

## Summary
Severity: Medium
Advisory: GHSA-g9w4-prf3-m25g
CVE: CVE-2023-38509
CWE: CWE-402
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-27
Source: https://github.com/advisories/GHSA-g9w4-prf3-m25g
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=3.5-milestone-1 <14.10.9
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=15.0 <15.3-rc-1

## Details
## Impact

The mail obfuscation configuration was not fully taken into account and is was still possible by obfuscated emails.

See https://jira.xwiki.org/browse/XWIKI-20601 for the reproduction steps.

## Patches

This has been patched in XWiki 14.10.9, and XWiki 15.3-rc-1.

## Workarounds

The workaround is to modify the page XWiki.LiveTableResultsMacros following this [patch](https://github.com/xwiki/xwiki-platform/commit/1dfb6804d4d412794cbe0098d4972b8ac263df0c).

## References

- https://jira.xwiki.org/browse/XWIKI-20601
- https://github.com/xwiki/xwiki-platform/commit/1dfb6804d4d412794cbe0098d4972b8ac263df0c

## For more information

If you have any questions or comments about this advisory:

-    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
-    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-g9w4-prf3-m25g
- https://nvd.nist.gov/vuln/detail/CVE-2023-38509
- https://github.com/xwiki/xwiki-platform/commit/1dfb6804d4d412794cbe0098d4972b8ac263df0
- https://github.com/xwiki/xwiki-platform/commit/1dfb6804d4d412794cbe0098d4972b8ac263df0c
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20601
