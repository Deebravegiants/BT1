# [C] XWiki Platform has an Unauthenticated XAR Import via REST /wikis/{wikiName}

## Summary
Severity: Critical
Advisory: GHSA-qrvh-r3f2-9h4r
CVE: CVE-2026-33137
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-qrvh-r3f2-9h4r
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=15.10.6 <16.10.17
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=17.0.0-rc-1 <17.4.9
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=17.5.0 <17.10.3
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=18.0.0-rc-1 <18.1.0-rc-1

## Details
### Impact

`POST /wikis/{wikiName}` executes a XAR import without performing any authentication or authorization checks, allowing an unauthenticated attacker to create or update documents in the target wiki

### Patches

This vulnerability has been patched in XWiki 16.10.17, 17.4.9, 17.10.3, 18.0.1 and 18.1.0-rc-1.

### Workarounds

XWiki is not aware of any workarounds other than adding a rule into an HTTP proxy to prevent access POST request in the `/wikis/{wikiName}[/]` endpoint.

### Resources

* https://jira.xwiki.org/browse/XWIKI-23953
* https://github.com/xwiki/xwiki-platform/commit/4b7b95b79256374d487e9ece1dc48f527966990f

### For more information

If there are any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Send an email to the [Security Mailing List](mailto:security@xwiki.org)

### Attribution

Reported by Sho Odagiri (GMO Cybersecurity by Ierae, Inc.).

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-qrvh-r3f2-9h4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33137
- https://github.com/xwiki/xwiki-platform/commit/4b7b95b79256374d487e9ece1dc48f527966990f
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23953
