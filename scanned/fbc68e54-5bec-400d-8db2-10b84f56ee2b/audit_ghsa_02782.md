# [C] Improper Access Control in jupyterhub-firstuseauthenticator

## Summary
Severity: Critical
Advisory: GHSA-5xvc-vgmp-jgc3
CVE: CVE-2021-41194
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-10-28
Source: https://github.com/advisories/GHSA-5xvc-vgmp-jgc3
Type: github-advisory

## Affected
- PyPI: `jupyterhub-firstuseauthenticator` — affected >=0 <1.0.0

## Details
### Impact

When JupyterHub is used with FirstUseAuthenticator, the vulnerability allows unauthorized access to any user's account if `create_users=True` and the username is known or guessed.

### Patches

Upgrade to jupyterhub-firstuseauthenticator to 1.0, or apply patch https://github.com/jupyterhub/firstuseauthenticator/pull/38.patch

### Workarounds

If you cannot upgrade, there is no complete workaround, but it can be mitigated.

If you cannot upgrade yet, you can disable user creation with `c.FirstUseAuthenticator.create_users = False`, which will only allow login with fully normalized usernames for already existing users prior to jupyterhub-firstuserauthenticator 1.0. If any users have never logged in with their normalized username (i.e. lowercase), they will still be vulnerable until you can patch or upgrade.

## References
- https://github.com/jupyterhub/firstuseauthenticator/security/advisories/GHSA-5xvc-vgmp-jgc3
- https://nvd.nist.gov/vuln/detail/CVE-2021-41194
- https://github.com/jupyterhub/firstuseauthenticator/pull/38
- https://github.com/jupyterhub/firstuseauthenticator/pull/38.patch
- https://github.com/jupyterhub/firstuseauthenticator/pull/38/commits/32b21898fb2b53b1a2e36270de6854ad70e9e9bf
- https://github.com/jupyterhub/firstuseauthenticator/pull/38/commits/9e200d974e0cb85d828a6afedb8ab90a37878f28
- https://github.com/jupyterhub/firstuseauthenticator/commit/953418e2450dbc2d854e332350849533b0ebc7ba
- https://github.com/jupyterhub/firstuseauthenticator
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterhub-firstuseauthenticator/PYSEC-2021-384.yaml
