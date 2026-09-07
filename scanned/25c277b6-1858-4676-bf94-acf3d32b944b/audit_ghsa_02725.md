# [M] No CSRF protection on the password change form

## Summary
Severity: Medium
Advisory: GHSA-v9j2-q4q5-cxh4
CVE: CVE-2021-32730
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-v9j2-q4q5-cxh4
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=0 <12.10.5
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=13.0 <13.2

## Details
### Impact
It's possible for forge an URL that, when accessed by an admin, will reset the password of any user in XWiki.

### Patches
The problem has been patched in XWiki 12.10.5, 13.2RC1.

### Workarounds
It's possible to apply the patch manually by modifying the `register_macros.vm` template like in https://github.com/xwiki/xwiki-platform/commit/0a36dbcc5421d450366580217a47cc44d32f7257.

### References
https://jira.xwiki.org/browse/XWIKI-18315

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-v9j2-q4q5-cxh4
- https://nvd.nist.gov/vuln/detail/CVE-2021-32730
- https://github.com/xwiki/xwiki-platform/commit/0a36dbcc5421d450366580217a47cc44d32f7257
- https://jira.xwiki.org/browse/XWIKI-18315
