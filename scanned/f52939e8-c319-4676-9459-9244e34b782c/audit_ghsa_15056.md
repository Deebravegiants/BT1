# [H] XWiki vulnerable to Denial of Service attack through attachments

## Summary
Severity: High
Advisory: GHSA-8959-rfxh-r4j4
CVE: CVE-2024-21651
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-08
Source: https://github.com/advisories/GHSA-8959-rfxh-r4j4
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-distribution-war` — affected >=14.10 <14.10.18
- Maven: `org.xwiki.platform:xwiki-platform-distribution-war` — affected >=15.0-rc-1 <15.5.3
- Maven: `org.xwiki.platform:xwiki-platform-distribution-war` — affected >=15.6-rc-1 <15.8-rc-1

## Details
### Impact

A user able to attach a file to a page can post a malformed TAR file by manipulating file modification times headers, which when parsed by Tika, could cause a denial of service issue via CPU consumption. 

### Patches
This vulnerability has been patched in XWiki 14.10.18, 15.5.3 and 15.8 RC1.

### Workarounds

The workaround is to download [commons-compress 1.24](https://search.maven.org/remotecontent?filepath=org/apache/commons/commons-compress/1.24.0/commons-compress-1.24.0.jar) and replace the one located in XWiki `WEB-INF/lib/` folder.

### References

https://jira.xwiki.org/browse/XCOMMONS-2796

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-8959-rfxh-r4j4
- https://nvd.nist.gov/vuln/detail/CVE-2024-21651
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XCOMMONS-2796
- https://search.maven.org/remotecontent?filepath=org/apache/commons/commons-compress/1.24.0/commons-compress-1.24.0.jar
