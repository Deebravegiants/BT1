# [M] Argo CD leaks repository credentials in user-facing error messages and in logs

## Summary
Severity: Medium
Advisory: GHSA-mv6w-j4xc-qpfw
CVE: CVE-2023-25163
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-mv6w-j4xc-qpfw
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.6.0-rc1 <2.6.1

## Details
### Impact
All versions of Argo CD starting with v2.6.0-rc1 have an output sanitization bug which leaks repository access credentials in error messages. These error messages are visible to the user, and they are logged. The error message is visible when a user attempts to create or update an Application via the Argo CD API (and therefor the UI or CLI). The user must have `applications, create` or `applications, update` RBAC access to reach the code which may produce the error.

The user is not guaranteed to be able to trigger the error message. They may attempt to spam the API with requests to trigger a rate limit error from the upstream repository. 

If the user has `repositories, update` access, they may edit an existing repository to introduce a URL typo or otherwise force an error message. But if they have that level of access, they are probably intended to have access to the credentials anyway.

### Patches

A patch for this vulnerability has been released in the following Argo CD version:

* v2.6.1

### Workarounds

The only way to completely resolve the issue is to upgrade.

#### Mitigations

To mitigate the issue, make sure that your repo credentials have only least necessary privileges. For example, the credentials should not have push access, and they should not have access to more resources than what Argo CD actually needs (for example, a whole GitHub org when only one repo is needed).

To further mitigate the impact of a leaked write-capable repo credential, you could [enable commit signature verification](https://argo-cd.readthedocs.io/en/stable/user-guide/gpg-verification/#enforcing-signature-verification). Even if someone could push a malicious commit, the commit would not by synced.

You should also enforce least privileges in Argo CD RBAC. Make sure users only have `repositories, update`, `applications, update`, or `applications, create` access if they absolutely need it.

### References

* The problem was initially reported in a [GitHub issue](https://github.com/argoproj/argo-cd/issues/12309)
* [Argo CD RBAC configuration documentation](https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/)

### For more information

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-mv6w-j4xc-qpfw
- https://nvd.nist.gov/vuln/detail/CVE-2023-25163
- https://github.com/argoproj/argo-cd/issues/12309
- https://github.com/argoproj/argo-cd/pull/12320
- https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac
- https://github.com/argoproj/argo-cd
- https://pkg.go.dev/vuln/GO-2023-1548
