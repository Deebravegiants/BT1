# [H] XWiki Platform Security Parent POM vulnerable to overwriting of security rules of a page with a final page having the same reference

## Summary
Severity: High
Advisory: GHSA-gg53-wf5x-r3r6
CVE: CVE-2022-31167
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-09-20
Source: https://github.com/advisories/GHSA-gg53-wf5x-r3r6
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-security` — affected >=5.0 <12.10.11
- Maven: `org.xwiki.platform:xwiki-platform-security` — affected >=13.0 <13.4.6
- Maven: `org.xwiki.platform:xwiki-platform-security` — affected >=13.10 <13.10.1

## Details
### Impact

A bug in the security cache is storing rules associated to document Page1.Page2 and space Page1.Page2 in the same cache entry.

That means that it's possible to overwrite the rights of a space or a document by creating the page of the space with the same name and checking the right of the new one first so that they end up in the security cache and are used for the other too.

### Patches

The problem has been patched in XWiki 12.10.11, 13.10.1, 13.4.6.

### Workarounds

No workaround other than patching.

### References

https://jira.xwiki.org/browse/XWIKI-14075
https://jira.xwiki.org/browse/XWIKI-18983

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gg53-wf5x-r3r6
- https://nvd.nist.gov/vuln/detail/CVE-2022-31167
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-14075
- https://jira.xwiki.org/browse/XWIKI-18983
