# [H] XWiki users registered with email verification can self re-activate their disabled accounts

## Summary
Severity: High
Advisory: GHSA-76mp-659p-rw65
CVE: CVE-2021-32620
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-76mp-659p-rw65
Type: github-advisory

## Affected
- Maven: `org.xwiki.commons:xwiki-commons-core` — affected >=11.6 <11.10.13
- Maven: `org.xwiki.commons:xwiki-commons-core` — affected >=12.0 <12.6.7
- Maven: `org.xwiki.commons:xwiki-commons-core` — affected >=12.10.0 <12.10.2

## Details
### Impact
A user disabled on a wiki using email verification for registration can re-activate himself by using the activation link provided for his registration. 

### Patches
The problem has been patched in the following versions of XWiki: 11.10.13,  12.6.7, 12.10.2, 13.0.

### Workarounds
It's possible to workaround the issue by resetting the `validkey` property of the disabled XWiki users. This can be done by editing the user profile with object editor.

### References
https://jira.xwiki.org/browse/XWIKI-17942

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](http://jira.xwiki.org)
* Email us at [Security mailing-list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-76mp-659p-rw65
- https://nvd.nist.gov/vuln/detail/CVE-2021-32620
- https://github.com/xwiki/xwiki-platform/commit/f9a677408ffb06f309be46ef9d8df1915d9099a4
- https://github.com/xwiki/xwiki-commons
- https://jira.xwiki.org/browse/XWIKI-17942
