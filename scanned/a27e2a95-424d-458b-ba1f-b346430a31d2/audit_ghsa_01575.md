# [H] RCE in XWiki

## Summary
Severity: High
Advisory: GHSA-5hv6-mh8q-q9v8
CVE: CVE-2020-15252
CWE: CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-10-16
Source: https://github.com/advisories/GHSA-5hv6-mh8q-q9v8
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <11.10.6
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=12.0 <12.5

## Details
### Impact

Any user with SCRIPT right (EDIT right before XWiki 7.4) can gain access to the application server Servlet context which contains tools allowing to instantiate arbitrary Java objects and invoke methods that may lead to arbitrary code execution.

### Patches

It has been patched in both version XWiki 12.5 and XWiki 11.10.6.

### Workarounds

The only workaround is to give SCRIPT right only to trusted users.

### References

https://jira.xwiki.org/browse/XWIKI-17423

It's been reported by the GitHub Security Lab under https://jira.xwiki.org/browse/XWIKI-17141.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [our security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-5hv6-mh8q-q9v8
- https://nvd.nist.gov/vuln/detail/CVE-2020-15252
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-17141
- https://jira.xwiki.org/browse/XWIKI-17423
