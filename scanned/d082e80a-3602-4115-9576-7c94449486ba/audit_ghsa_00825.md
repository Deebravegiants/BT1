# [M] CSRF vulnerability in save-server

## Summary
Severity: Medium
Advisory: GHSA-wwrj-35w6-77ff
CVE: CVE-2020-15135
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2020-08-04
Source: https://github.com/advisories/GHSA-wwrj-35w6-77ff
Type: github-advisory

## Affected
- npm: `save-server` — affected >=0 <1.0.7

## Details
### Impact
Versions prior to version v1.05 are affected by a CSRF vulnerability, as there is no CSRF mitigation (Tokens etc.). The fix introduced in version v1.05 unintentionally breaks uploading so version v1.0.7 is the fixed version.

This is patched by implementing [Double submit](https://medium.com/cross-site-request-forgery-csrf/double-submit-cookie-pattern-65bb71d80d9f).

The CSRF attack would require you to navigate to a malicious site while you have an active session with Save-Server (Session key stored in cookies). The malicious user would then be able to perform some actions, including:
- Upload file
- Delete file
- Add redirect


#### If you are logged in as root, this attack is significantly more severe. They can (in addition to the above):
- Create users
- Delete users
- Update users (change password)

If they updated the password of a user, that user's files would then be available. If the root password is updated, all files would be visible if they logged in with the new password.

Note that due to the same origin policy malicious actors cannot view the gallery or the response of any of the methods, nor be sure they succeeded. 
### Patches
This issue has been patched. Update to version v1.0.7 or above to benefit from this fix.

### Workarounds
None. You should upgrade.

### References
What is CSRF: https://owasp.org/www-community/attacks/csrf
Fix type: https://medium.com/cross-site-request-forgery-csrf/double-submit-cookie-pattern-65bb71d80d9f

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Save-server](https://github.com/Neztore/save-server/)
* Email us at [hi@nezto.re](mailto:hi@nezto.re)
* Join our discord (preferred): [Invite](https://discord.gg/QevWabU)

## References
- https://github.com/Neztore/save-server/security/advisories/GHSA-wwrj-35w6-77ff
- https://nvd.nist.gov/vuln/detail/CVE-2020-15135
- https://medium.com/cross-site-request-forgery-csrf/double-submit-cookie-pattern-65bb71d80d9f
- https://www.npmjs.com/package/save-server
