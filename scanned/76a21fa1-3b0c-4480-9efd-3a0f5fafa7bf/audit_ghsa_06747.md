# [H] XWiki Platform Old Core: Resource path traversal via /skin/ action endpoint in Jetty 12+

## Summary
Severity: High
Advisory: GHSA-qj4x-9g63-25g6
CVE: CVE-2026-34151
CWE: CWE-24
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-qj4x-9g63-25g6
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <17.10.5
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=18.0.0-rc-1 <18.2.0

## Details
### Impact

With Jetty 12+ a user can craft a URL to access any resource the Jetty instance is allowed to access.

For example `http://[host]/xwiki/bin/skin/..%252f/..%252f..%252f..%252f..%252f..%252f..%252f..%252fetc/passwd` allows downloading the content of the /etc/passwd file, provided Jetty is allowed to read it, and if your XWiki webapp is located exactly 5 levels below `/` (like `/var/lib/jetty/webapps/xwiki`, which is the case in the docker image, for example).

Another example which does not go out of the XWiki webapp, but it's still a vulnerability (since users should not be allowed to access Hibernate or XWiki configuration files) is `http://[host]/xwiki/bin/skin/..%252f/..%252fWEB-INF/xwiki.cfg`.

### Patches

This vulnerability has been patched in XWiki 17.10.5 and 18.2.0.

### Workarounds

A possible workaround is to use a different application server, like Jetty < 12 (in the case of XWiki < 17) or Tomcat, which don't seem to be impacted.

### Resources

* https://jira.xwiki.org/browse/XWIKI-24075
* https://jira.xwiki.org/browse/XCOMMONS-3594

### For more information

If there are any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Send an email to the [Security Mailing List](mailto:security@xwiki.org)

### Attribution

 Lê Ngọc Khoa reported the vulnerability.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-qj4x-9g63-25g6
- https://github.com/xwiki/xwiki-commons/pull/1675
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XCOMMONS-3594
- https://jira.xwiki.org/browse/XWIKI-24075
