# [M] The reset password form reveal users email address

## Summary
Severity: Medium
Advisory: GHSA-h4m4-pgp4-whgm
CVE: CVE-2021-32731
CWE: CWE-200, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-h4m4-pgp4-whgm
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=13.1 <13.2

## Details
### Impact
The reset password form reveals the email address of users just by giving their username.

### Patches
The problem has been patched on XWiki 13.2RC1.

### Workarounds
It's possible to manually modify the `resetpasswordinline.vm` to perform the changes made in https://github.com/xwiki/xwiki-platform/commit/0cf716250b3645a5974c80d8336dcdf885749dff#diff-14a3132e3986b1f5606dd13d9d8a8bb8634bec9932123c5e49e9604cfd850fc2

### References
https://jira.xwiki.org/browse/XWIKI-18400

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xiwki.org)
* Email us at [Security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h4m4-pgp4-whgm
- https://nvd.nist.gov/vuln/detail/CVE-2021-32731
- https://github.com/xwiki/xwiki-platform/commit/0cf716250b3645a5974c80d8336dcdf885749dff#diff-14a3132e3986b1f5606dd13d9d8a8bb8634bec9932123c5e49e9604cfd850fc2
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18400
