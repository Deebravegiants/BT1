# [M] XWiki PlantUML Macro Vulnerable to Server-Side Request Forgery (SSRF) via 'server' parameter

## Summary
Severity: Medium
Advisory: GHSA-42fc-7w97-8vrc
CVE: CVE-2026-42140
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-42fc-7w97-8vrc
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.plantuml:macro-plantuml-macro` — affected >=0 <2.4.1

## Details
### Impact

The [PlantUML Macro](https://extensions.xwiki.org/xwiki/bin/view/Extension/PlantUML+Macro) is vulnerable to Server-Side Request Forgery (SSRF). The macro allows users to specify an alternative PlantUML server via the `server` parameter. However, the application does not validate the supplied URL. An attacker can supply an internal IP address or a malicious external URL. The XWiki server will attempt to connect to this URL to "render" the diagram.

This issue affects all versions of the Plant UML Macro extension till version 2.4 included.

### Patches

Version 2.4.1 of the Plant UML Macro extension fixes the issue by verifying if the supplied server domain matches one of the [trusted domain configured inside of XWiki](https://www.xwiki.org/xwiki/bin/view/Documentation/AdminGuide/Configuration/#HTrusteddomains).

### Workarounds

Protect the XWiki server by placing it in a DMZ so that it cannot access any other internal servers.

### Resources

The issue was fixed in [PLANTUML-25](https://jira.xwiki.org/browse/PLANTUML-25) by the commit [c8b19bda93058794e04c8862fc7ca85c59b5fe5c](https://github.com/xwiki-contrib/macro-plantuml/commit/c8b19bda93058794e04c8862fc7ca85c59b5fe5c).

### For more information

If there are any questions or comments about this advisory:
* Open an issue in [JIRA XWiki.org](https://jira.xwiki.org/)
* Send an email to [Security Mailing List](mailto:security@xwiki.org)

### Attribution

The issue was reported by Łukasz Rybak.

## References
- https://github.com/xwiki-contrib/macro-plantuml/security/advisories/GHSA-42fc-7w97-8vrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42140
- https://github.com/xwiki-contrib/macro-plantuml/commit/c8b19bda93058794e04c8862fc7ca85c59b5fe5c
- https://github.com/xwiki-contrib/macro-plantuml
- https://jira.xwiki.org/browse/PLANTUML-25
