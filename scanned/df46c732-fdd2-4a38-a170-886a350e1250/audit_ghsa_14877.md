# [H] Globus `identity_provider` restriction ignored when used with `allow_all` in JupyterHub 5.0

## Summary
Severity: High
Advisory: GHSA-gprj-3p75-f996
CVE: CVE-2024-37300
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-12
Source: https://github.com/advisories/GHSA-gprj-3p75-f996
Type: github-advisory

## Affected
- PyPI: `oauthenticator` — affected >=0 <16.3.1

## Details
### Impact

JupyterHub < 5.0, when used with `GlobusOAuthenticator`, could be configured to allow all users from a particular institution only. The configuration for this would look like:

```python
# Require users to be using the "foo.horse" identity provider, often an institution or university
c.GlobusAuthenticator.identity_provider = "foo.horse"
# Allow everyone who has that identity provider to log in
c.GlobusAuthenticator.allow_all = True
```

This worked fine prior to JupyterHub 5.0, because `allow_all` *did not* take precedence over `identity_provider`.

Since JupyterHub 5.0, `allow_all` *does* take precedence over `identity_provider`. On a hub with the same config, now **all** users will be allowed to login, regardless of `identity_provider`. `identity_provider` will basically be ignored.

This is a [documented change](https://jupyterhub.readthedocs.io/en/stable/howto/upgrading-v5.html#authenticator-allow-all-and-allow-existing-users) in JupyterHub 5.0,
but is likely to catch many users by surprise.

### Patches

OAuthenticator 16.3.1 fixes the issue with JupyterHub 5.0, and does not affect previous versions.

### Workarounds

Do not upgrade to JupyterHub 5.0 when using `GlobusOAuthenticator` in the prior configuration.

## References
- https://github.com/jupyterhub/oauthenticator/security/advisories/GHSA-gprj-3p75-f996
- https://nvd.nist.gov/vuln/detail/CVE-2024-37300
- https://github.com/jupyterhub/oauthenticator/commit/d1aea05fa89f2beae15ab0fa0b0d071030f79654
- https://github.com/jupyterhub/oauthenticator
- https://jupyterhub.readthedocs.io/en/stable/howto/upgrading-v5.html#authenticator-allow-all-and-allow-existing-users
