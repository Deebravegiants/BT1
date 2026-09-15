# [H] XWiki Platform may retrieve email addresses of all users 

## Summary
Severity: High
Advisory: GHSA-7vr7-cghh-ch63
CVE: CVE-2023-34467
CWE: CWE-402, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-7vr7-cghh-ch63
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=3.5-milestone-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=14.5 <14.10.4

## Details
### Impact
The mail obfuscation configuration was not fully taken into account and while the mail displayed to the end user was obfuscated:
- the rest response was also containing the mail unobfuscated
- user were able to filter and sort on the unobfuscated (allowing to infer the mail content)

The consequence was the possibility to retrieve the email addresses of all users even when obfuscated.

See https://jira.xwiki.org/browse/XWIKI-20333 for the reproduction steps.

### Patches
This has been patched in XWiki 14.10.4, XWiki 14.4.8, and XWiki 15.0-rc-1.

### Workarounds
The workaround is to modify the page `XWiki.LiveTableResultsMacros` following this [patch](https://github.com/xwiki/xwiki-platform/commit/71f889db9962df2d385f4298e29cfbc9050b828a#diff-5a739e5865b1f1ad9d79b724791be51b0095a0170cc078911c940478b13b949a).

### References

https://jira.xwiki.org/browse/XWIKI-20333

### For more information

If you have any questions or comments about this advisory:

*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been reported on Intigriti by @floerer

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-7vr7-cghh-ch63
- https://nvd.nist.gov/vuln/detail/CVE-2023-34467
- https://github.com/xwiki/xwiki-platform/commit/71f889db9962df2d385f4298e29cfbc9050b828a#diff-5a739e5865b1f1ad9d79b724791be51b0095a0170cc078911c940478b13b949a
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20333
