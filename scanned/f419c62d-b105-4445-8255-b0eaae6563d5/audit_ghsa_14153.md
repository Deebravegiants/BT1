# [M] org.xwiki.platform:xwiki-platform-oldcore Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6gvj-8vc5-8v3j
CVE: CVE-2023-32068
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-15
Source: https://github.com/advisories/GHSA-6gvj-8vc5-8v3j
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <14.10.4

## Details
### Impact

It's possible to exploit well known parameters in XWiki URLs to perform redirection to untrusted site. This vulnerability was partially fixed in the past for XWiki 12.10.7 and 13.3RC1 but there is still the possibility to force specific URLs to skip some checks, e.g. using URLs like `http:example.com` in the parameter would allow the redirect. 

### Patches

The issue has now been patched against all patterns that we know about for performing redirect. It also performs a real URI parsing that should protect in most cases. This has been patched in XWiki 14.10.4 and 15.0. 

### Workarounds

The only workaround is to upgrade XWiki.

### References

  * JIRA ticket: https://jira.xwiki.org/browse/XWIKI-20096
  * JIRA ticket about the improvment actually fixing the vulnerability: https://jira.xwiki.org/browse/XWIKI-20549
  * Previous advisory about open redirect: https://github.com/advisories/GHSA-jp55-vvmf-63mv

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## Attribution 

Thanks to Paulos Mesfin who originally reported the vulnerability.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-6gvj-8vc5-8v3j
- https://nvd.nist.gov/vuln/detail/CVE-2023-32068
- https://github.com/xwiki/xwiki-platform/commit/e4f7f68e93cb08c25632c126356d218abf192d1e
- https://github.com/advisories/GHSA-jp55-vvmf-63mv
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20096
- https://jira.xwiki.org/browse/XWIKI-20549
