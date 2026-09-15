# [H] CSRF can expose users authentication token

## Summary
Severity: High
Advisory: GHSA-hh7m-rx4f-4vpv
CVE: CVE-2021-21241
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-01-11
Source: https://github.com/advisories/GHSA-hh7m-rx4f-4vpv
Type: github-advisory

## Affected
- PyPI: `Flask-Security-Too` — affected >=3.3.0 <3.4.5

## Details
### Issue
The  /login and /change endpoints can return the authenticated user's authentication token in response to a GET request. Since GET requests aren't protected with a CSRF token, this could lead to a malicious 3rd party site acquiring the authentication token.

### Patches
Version 3.4.5 and soon to be released 4.0.0 are patched.

### Workarounds
If you aren't using authentication tokens - you can set the SECURITY_TOKEN_MAX_AGE to "0" (seconds) which should make the token unusable.

### References
None

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21241
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-security-too/PYSEC-2021-91.yaml
- https://pypi.org/project/Flask-Security-Too
- https://web.archive.org/web/20210118165844/https://github.com/Flask-Middleware/flask-security/releases/tag/3.4.5
- https://web.archive.org/web/20210118165958/https://github.com/Flask-Middleware/flask-security/commit/6d50ee9169acf813257c37b75babe9c28e83542a
- https://web.archive.org/web/20210118170445/https://github.com/Flask-Middleware/flask-security/commit/61d313150b5f620d0b800896c4f2199005e84b1f
- https://web.archive.org/web/20210118170502/https://github.com/Flask-Middleware/flask-security/security/advisories/GHSA-hh7m-rx4f-4vpv
- https://web.archive.org/web/20211207005640/https://github.com/Flask-Middleware/flask-security/pull/422
