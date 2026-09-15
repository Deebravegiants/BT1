# [M] User with permission to write actions can impersonate another user when auth token is configured in environment variable

## Summary
Severity: Medium
Advisory: GHSA-26hr-q2wp-rvc5
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-26hr-q2wp-rvc5
Type: github-advisory

## Affected
- Go: `github.com/treeverse/lakefs` — affected >=0 <1.3.1

## Details
### Impact

When lakeFS is configured with **ALL** of the following:

- Configuration option `auth.encrypt.secret_key` passed through environment variable
- Actions enabled via configuration option `actions.enabled` (default enabled)

then a user who can configure an action can impersonate any other user.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

### Workarounds

**ANY ONE** of these is sufficient to prevent the issue:

* Do not pass `auth.encrypt.secret_key` through an environment variable.

   For instance, Kubernetes users can generate the entire configuration as a secret and mount that.  This is described [here](https://kubernetes.io/docs/concepts/configuration/secret/#using-a-secret).
* Disable actions.
* Limit users allowed to configure actions.

## References
- https://github.com/treeverse/lakeFS/security/advisories/GHSA-26hr-q2wp-rvc5
- https://github.com/treeverse/lakeFS
