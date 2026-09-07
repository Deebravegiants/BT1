# [C] XWiki configuration files can be accessed through the webjars API

## Summary
Severity: Critical
Advisory: GHSA-qww7-89xh-x7m7
CVE: CVE-2025-55747
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-qww7-89xh-x7m7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-webjars-api` — affected >=7.1.4 <16.10.7
- Maven: `org.xwiki.platform:xwiki-platform-webjars-api` — affected >=17.0.0-rc-1 <17.4.0-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-webjars` — affected >=6.1-miletone-2

## Details
### Impact

It's possible to get access and read configuration files by using URLs such as http://localhost:8080/xwiki/webjars/wiki%3Axwiki/..%2F..%2F..%2F..%2F..%2FWEB-INF%2Fxwiki.cfg. The trick here is to encode the / which is decoded when parsing the URL segment, but not re-encoded when assembling the file path.

### Patches

This has been patched in 17.4.0-rc-1, 16.10.7.

### Workarounds

There is no known workaround, other than upgrading XWiki.

### References

* https://jira.xwiki.org/browse/XWIKI-19350
* https://github.com/xwiki/xwiki-platform/commit/9e7b4c03f2143978d891109a17159f73d4cdd318#diff-45ea9c87d5fb68cd5db0da7f78cf25e76f1325f5fe56e21618b21786fc706236R80-R81

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-qww7-89xh-x7m7
- https://nvd.nist.gov/vuln/detail/CVE-2025-55747
- https://github.com/xwiki/xwiki-platform/commit/9e7b4c03f2143978d891109a17159f73d4cdd318#diff-45ea9c87d5fb68cd5db0da7f78cf25e76f1325f5fe56e21618b21786fc706236R80-R81
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19350
