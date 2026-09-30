# [C] XWiki Platform has path traversal via resources parameter in ssx and jsx endpoints when using leading slash

## Summary
Severity: Critical
Advisory: GHSA-xq3r-2qv5-vqqm
CVE: CVE-2026-23734
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-xq3r-2qv5-vqqm
Type: github-advisory

## Affected
- Maven: `org.xwiki.commons:xwiki-commons-classloader-api` — affected >=4.2-milestone-2 <16.10.17
- Maven: `org.xwiki.commons:xwiki-commons-classloader-api` — affected >=17.0.0-rc-1 <17.4.9
- Maven: `org.xwiki.commons:xwiki-commons-classloader-api` — affected >=17.5.0 <17.10.3
- Maven: `org.xwiki.commons:xwiki-commons-classloader-api` — affected >=18.0.0-rc-1 <18.1.0-rc-1

## Details
### Impact

It's possible to get access and read configuration files by using URLs such as `http://localhost:8080/bin/ssx/Main/WebHome?resource=/../../WEB-INF/xwiki.cfg&minify=false`.

This can apparently be reproduced on Tomcat instances.

### Patches

This has been patched in 18.0.0-rc-1, 17.10.3, 17.4.9, 16.10.17.

### Workarounds

There is no known workaround, other than upgrading XWiki.

### References

* https://jira.xwiki.org/browse/XCOMMONS-3547
* https://github.com/xwiki/xwiki-commons/commit/a979cafd89f6a9c9c0b9ab19744d672df64429bf

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

The vulnerability was reported by Michał Kołek.

## References
- https://github.com/xwiki/xwiki-commons/security/advisories/GHSA-xq3r-2qv5-vqqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-23734
- https://github.com/xwiki/xwiki-commons/commit/a979cafd89f6a9c9c0b9ab19744d672df64429bf
- https://github.com/xwiki/xwiki-commons
- https://jira.xwiki.org/browse/XCOMMONS-3547
