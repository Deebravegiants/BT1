# [C] XWiki Platform vulnerable to cross-site request forgery (CSRF) via the REST API

## Summary
Severity: Critical
Advisory: GHSA-6xxr-648m-gch6
CVE: CVE-2023-37277
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-10
Source: https://github.com/advisories/GHSA-6xxr-648m-gch6
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=1.8 <14.10.8
- Maven: `com.xpn.xwiki.platform:xwiki-core-rest-server` — affected >=1.8 <14.10.8
- Maven: `com.xpn.xwiki.platform:xwiki-rest` — affected >=1.8 <14.10.8
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=15.0-rc-1 <15.2

## Details
### Impact

The REST API allows executing all actions via POST requests and accepts `text/plain`, `multipart/form-data` or `application/www-form-urlencoded` as content types which can be sent via regular HTML forms, thus allowing cross-site request forgery. With the interaction of a user with programming rights, this allows remote code execution through script macros and thus impacts the integrity, availability and confidentiality of the whole XWiki installation.

For regular cookie-based authentication, the vulnerability is mitigated by SameSite cookie restrictions but as of March 2023, these are not enabled by default in Firefox and Safari.

### Patches
The vulnerability has been patched in XWiki 14.10.8 and 15.2 by requiring a CSRF token header for certain request types that are susceptible to CSRF attacks.

### Workarounds

It is possible to check for the `Origin` header in a reverse proxy to protect the REST endpoint from CSRF attacks, see [the Jira issue](https://jira.xwiki.org/browse/XWIKI-20135) for an example configuration.

### References

* https://jira.xwiki.org/browse/XWIKI-20135
* https://github.com/xwiki/xwiki-platform/commit/4c175405faa0e62437df397811c7526dfc0fbae7

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-6xxr-648m-gch6
- https://nvd.nist.gov/vuln/detail/CVE-2023-37277
- https://github.com/xwiki/xwiki-platform/commit/4c175405faa0e62437df397811c7526dfc0fbae7
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20135
