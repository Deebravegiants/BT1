# [H] XWiki Jetty Package (XJetty) allows accessing any application file through URL

## Summary
Severity: High
Advisory: GHSA-53gx-j3p6-2rw9
CVE: CVE-2025-55749
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-01
Source: https://github.com/advisories/GHSA-53gx-j3p6-2rw9
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-tool-jetty-resources` — affected >=16.7.0 <16.10.11
- Maven: `org.xwiki.platform:xwiki-platform-tool-jetty-resources` — affected >=17.0.0-rc-1 <17.4.4
- Maven: `org.xwiki.platform:xwiki-platform-tool-jetty-resources` — affected >=17.5.0 <17.7.0

## Details
### Impact

In an instance which is using the XWiki Jetty package (XJetty), a context is exposed to statically access any file located in the webapp/ folder.

It allows accessing files which might contains credentials, like http://myhots/webapps/xwiki/WEB-INF/xwiki.cfg, http://myhots/webapps/xwiki/WEB-INF/xwiki.properties or http://myhots/webapps/xwiki/WEB-INF/hibernate.cfg.xml.

### Patches

This has been patched in 16.10.11, 17.4.4, 17.7.0.

### Workarounds

The workaround is to modify the start_xwiki.sh script following https://github.com/xwiki/xwiki-platform/compare/8b68d8a70b43f25391b3ee48477d7eb71b95cf4b...99a04a0e2143583f5154a43e02174155da7e8e10.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

Vulnerability reported by Joseph Huber.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-53gx-j3p6-2rw9
- https://nvd.nist.gov/vuln/detail/CVE-2025-55749
- https://github.com/xwiki/xwiki-platform/commit/42fb063749dd88cc78196f72d7318b7179285ebd
- https://github.com/xwiki/xwiki-platform/commit/99a04a0e2143583f5154a43e02174155da7e8e10
- https://github.com/xwiki/xwiki-platform
- https://github.com/xwiki/xwiki-platform/compare/8b68d8a70b43f25391b3ee48477d7eb71b95cf4b...99a04a0e2143583f5154a43e02174155da7e8e10
- https://jira.xwiki.org/browse/XWIKI-23438
