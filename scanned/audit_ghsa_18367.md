# [C] XWiki configuration files can be accessed through jsx and sx endpoints

## Summary
Severity: Critical
Advisory: GHSA-m63c-3rmg-r2cf
CVE: CVE-2025-55748
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-m63c-3rmg-r2cf
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-skin-skinx` — affected >=4.2-milestone-2 <16.10.7

## Details
### Impact

It's possible to get access and read configuration files by using URLs such as `http://localhost:8080/bin/ssx/Main/WebHome?resource=../../WEB-INF/xwiki.cfg&minify=false`.

This can apparently be reproduced on Tomcat instances.

### Patches

This has been patched in  17.4.0-rc-1, 16.10.7.

### Workarounds

There is no known workaround, other than upgrading XWiki.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

The vulnerability was reported by Gregor Neumann.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-m63c-3rmg-r2cf
- https://nvd.nist.gov/vuln/detail/CVE-2025-55748
- https://github.com/xwiki/xwiki-platform/commit/9e7b4c03f2143978d891109a17159f73d4cdd318#diff-ee78930a9ac5ea586179fe8ab88a5fd58e369d175927d1e88a0b4dbc3ebcbf1eR62
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23109
