# [H] Base class whitelist configuration ignored in OAuthenticator

## Summary
Severity: High
Advisory: GHSA-384w-5v3f-q499
CVE: CVE-2020-26250
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-12-01
Source: https://github.com/advisories/GHSA-384w-5v3f-q499
Type: github-advisory

## Affected
- PyPI: `oauthenticator` — affected >=0.12.0 <0.12.2

## Details
### Impact

__What goes wrong?__

The deprecated (in jupyterhub 1.2) configuration `Authenticator.whitelist`, which should be transparently mapped to `Authenticator.allowed_users` with a warning, is instead ignored by OAuthenticator classes, resulting in the same behavior as if this configuration has not been set. If this is the only mechanism of authorization restriction (i.e. no group or team restrictions in configuration) then all authenticated users will be allowed. Provider-based restrictions, including deprecated values such as `GitHubOAuthenticator.org_whitelist` are **not** affected.

__Who is impacted?__

All users of OAuthenticator 0.12.0 and 0.12.1 with JupyterHub 1.2 (JupyterHub Helm chart 0.10.0-0.10.5) who use the `admin.whitelist.users` configuration in the jupyterhub helm chart or the `c.Authenticator.whitelist` configuration directly. Users of other deprecated configuration, e.g. `c.GitHubOAuthenticator.team_whitelist` are **not** affected.

If you see a log line like this and expect a specific list of allowed usernames:

```
[I 2020-11-27 16:51:54.528 JupyterHub app:1717] Not using allowed_users. Any authenticated user will be allowed.
```

you are likely affected.

### Patches

- Replacing deprecated `c.Authenticator.whitelist = ...` with `c.Authenticator.allowed_users = ...` avoids the issue.
- Update oauthenticator to 0.12.2
- Update jupyterhub helm chart to 0.10.6

If any users have been authorized during this time who should not have been, they must be deleted via the API or admin interface, [per the documentation](https://jupyterhub.readthedocs.io/en/1.2.2/getting-started/authenticators-users-basics.html#add-or-remove-users-from-the-hub).

### Workarounds

Replacing `c.Authenticator.whitelist = ...` with `c.Authenticator.allowed_users = ...` avoids the issue.

In the jupyterhub helm chart prior to 0.10.6, this can be done via `hub.extraConfig`:

```yaml
auth:
  allowedUsers:
  - user1
  - user2

hub:
  extraConfig:
    allowedUsers: |
        # set new field not exposed in helm chart < 0.10.6
        set_config_if_not_none(c.Authenticator, "allowed_users", "auth.allowedUsers")
```


### For more information

If you have any questions or comments about this advisory:

* Open a thread [on the Jupyter forum](http://discourse.jupyter.org)
* Email us at [security@ipython.org](mailto:security@ipython.org)

## References
- https://github.com/jupyterhub/oauthenticator/security/advisories/GHSA-384w-5v3f-q499
- https://nvd.nist.gov/vuln/detail/CVE-2020-26250
- https://github.com/jupyterhub/oauthenticator/commit/a4aac191c16cf6281f3d346615aefa75702b02d7
- https://github.com/jupyterhub/oauthenticator
- https://github.com/jupyterhub/oauthenticator/blob/master/docs/source/changelog.md#0122---2020-11-30
- https://github.com/pypa/advisory-database/tree/main/vulns/oauthenticator/PYSEC-2020-68.yaml
- https://jupyterhub.readthedocs.io/en/1.2.2/getting-started/authenticators-users-basics.html#add-or-remove-users-from-the-hub
