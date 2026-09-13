# [C] XWiki OIDC Authenticator vulnerable to bypassing OpenID login by providing a custom provider

## Summary
Severity: Critical
Advisory: GHSA-m7gv-v8xx-v47w
CVE: CVE-2022-39387
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-11-04
Source: https://github.com/advisories/GHSA-m7gv-v8xx-v47w
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.oidc:oidc-authenticator` — affected >=0 <1.29.1

## Details
### Impact

Even if a wiki has an OpenID provider configured through its xwiki.properties, it is possible to provide a third party provider by providing its details through request parameters. One can then bypass the XWiki authentication altogether by specifying its own provider through the oidc.endpoint.* request parameters (or by using an XWiki-based OpenID provider with oidc.xwikiprovider.

With the same approach, one could also provide a specific group mapping through oidc.groups.mapping that would make his user automatically part of the XWikiAdminGroup

### Patches

Patched in version 1.29.1.

### Workarounds

There is no workaround, an upgrade of the authenticator is required.

### References

https://jira.xwiki.org/browse/OIDC-118

### For more information

If you have any questions or comments about this advisory:

* Open an issue in Jira XWiki
* Email us at our security mailing list

## References
- https://github.com/xwiki-contrib/oidc/security/advisories/GHSA-m7gv-v8xx-v47w
- https://nvd.nist.gov/vuln/detail/CVE-2022-39387
- https://github.com/xwiki-contrib/oidc/commit/0247af1417925b9734ab106ad7cd934ee870ac89
- https://github.com/xwiki-contrib/oidc
- https://jira.xwiki.org/browse/OIDC-118
