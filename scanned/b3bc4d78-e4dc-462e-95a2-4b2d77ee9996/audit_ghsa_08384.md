# [H] Jupyter Server's Authentication Cookies Remain Valid After Password Reset and Server Restart

## Summary
Severity: High
Advisory: GHSA-5mrq-x3x5-8v8f
CVE: CVE-2026-40934
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-5mrq-x3x5-8v8f
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <2.18.0

## Details
## Summary

A persistent cookie secret vulnerability allows authenticated users to maintain indefinite access even after password changes. 

The cookie secret used to sign authentication cookies is stored in a permanent file (`~/.local/share/jupyter/runtime/jupyter_cookie_secret`) that is never automatically rotated or cleared, allowing stolen or compromised cookies to remain valid indefinitely regardless of password resets.

## PoC

- Start a Jupyter server with password authentication: `jupyter server password`, `jupyter server`
- Log in with the password and capture the authentication cookie (e.g., just login with a browser).
- Change the password to revoke access: `jupyter server password`
- Restart the server
- Use the old stolen cookie => remains valid and provides full authenticated access.

## Impact

- All jupyter-server deployments using password authentication where security incidents may occur
- Multi-user systems where one user's compromised session should be revocable by administrators
- Shared or public-facing Jupyter servers where credential rotation is a security requirement
- Any deployment where password changes are expected to revoke existing sessions

## Patches

Jupyter Server 2.18+

## Workaround

```bash
rm ~/.local/share/jupyter/runtime/jupyter_cookie_secret
# Then restart the server
```

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-5mrq-x3x5-8v8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-40934
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2026-69.yaml
