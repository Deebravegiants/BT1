# [M] Flask App Builder has an Authentication Bypass vulnerability when using non AUTH_DB methods

## Summary
Severity: Medium
Advisory: GHSA-765j-9r45-w2q2
CVE: CVE-2025-58065
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-765j-9r45-w2q2
Type: github-advisory

## Affected
- PyPI: `flask-appbuilder` — affected >=0 <4.8.1

## Details
### Impact
When Flask-AppBuilder is configured to use OAuth, LDAP, or other non-database authentication methods, the password reset endpoint remains registered and accessible, despite not being displayed in the user interface. This allows an enabled user to reset their password and be able to create JWT tokens even after the user is disabled on the authentication provider.

### Patches
Upgrade to Flask-AppBuilder version 4.8.1 or later

### Workarounds
If immediate upgrade is not possible:
- Manually disable password reset routes in the application configuration
- Implement additional access controls at the web server or proxy level to block access to the reset my password URL.
- Monitor for suspicious password reset attempts from disabled accounts

## References
- https://github.com/dpgaspar/Flask-AppBuilder/security/advisories/GHSA-765j-9r45-w2q2
- https://nvd.nist.gov/vuln/detail/CVE-2025-58065
- https://github.com/dpgaspar/Flask-AppBuilder/pull/2384
- https://github.com/dpgaspar/Flask-AppBuilder/commit/a942a9cc5775752f9a02f97fd8198dd288fa93ee
- https://github.com/dpgaspar/Flask-AppBuilder
- https://github.com/dpgaspar/Flask-AppBuilder/releases/tag/v4.8.1
