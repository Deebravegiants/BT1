# [H] JupyterHub has a privilege escalation vulnerability with the `admin:users` scope

## Summary
Severity: High
Advisory: GHSA-9x4q-3gxw-849f
CVE: CVE-2024-41942
CWE: CWE-274
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-08
Source: https://github.com/advisories/GHSA-9x4q-3gxw-849f
Type: github-advisory

## Affected
- PyPI: `jupyterhub` — affected >=0 <4.1.6
- PyPI: `jupyterhub` — affected >=5.0.0 <5.1.0

## Details
### Summary

If a user is granted the `admin:users` scope, they may escalate their own privileges by making themselves a full admin user.

### Details

The `admin:users` scope allows a user to edit user records:

> admin:users
>
> Read, write, create and delete users and their authentication state, not including their servers or tokens.
>
> -- https://jupyterhub.readthedocs.io/en/stable/rbac/scopes.html#available-scopes

However, this includes making users admins. Admin users are granted scopes beyond `admin:users` making this a mechanism by which granted scopes may be escalated.

### Impact

The impact is relatively small in that `admin:users` is already an extremely privileged scope only granted to trusted users.
In effect, `admin:users` is equivalent to `admin=True`, which is not intended.

Note that the change here only prevents escalation to the built-in JupyterHub admin role that has unrestricted permissions. It does not prevent users with e.g. `groups` permissions from granting themselves or other users permissions via group membership, which is intentional.

## References
- https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-9x4q-3gxw-849f
- https://nvd.nist.gov/vuln/detail/CVE-2024-41942
- https://github.com/jupyterhub/jupyterhub/commit/99e2720b0fc626cbeeca3c6337f917fdacfaa428
- https://github.com/jupyterhub/jupyterhub/commit/ff2db557a85b6980f90c3158634bf924063ab8ba
- https://github.com/jupyterhub/jupyterhub
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterhub/PYSEC-2024-200.yaml
