# [M] JupyterHub has Unauthenticated Denial of Service via Unbounded Username Logging on Failed Login

## Summary
Severity: Medium
Advisory: GHSA-p43p-whwx-q52h
CVE: CVE-2026-54338
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-p43p-whwx-q52h
Type: github-advisory

## Affected
- PyPI: `jupyterhub` — affected >=0 <5.5.0

## Details
### Impact

Invalid input to login resulted in unbounded logging output. Only form-based Authenticators (the default PAM Authenticator, but not the more widely used OAuthenticator) are affected.

### Patches

Upgrade to 5.5.0.

### Workarounds

Use an Authenticator that doesn't use a login form, such as OAuthenticator.

## References
- https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-p43p-whwx-q52h
- https://nvd.nist.gov/vuln/detail/CVE-2026-54338
- https://github.com/jupyterhub/jupyterhub/commit/d6dc595f84b7509969686da31d87d6d69e7fce0a
- https://github.com/jupyterhub/jupyterhub
