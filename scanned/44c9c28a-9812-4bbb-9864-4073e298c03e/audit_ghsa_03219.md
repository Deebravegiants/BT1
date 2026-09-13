# [M] Helm OCI credentials leaked into Argo CD logs

## Summary
Severity: Medium
Advisory: GHSA-6w87-g839-9wv7
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-6w87-g839-9wv7
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=0 <1.7.14
- Go: `github.com/argoproj/argo-cd` — affected >=1.8.0 <1.8.7

## Details
### Impact

When Argo CD was connected to a Helm OCI repository with authentication enabled, the credentials used for accessing the remote repository were logged.

Anyone with access to the pod logs - either via access with appropriate permissions to the Kubernetes control plane or a third party log management system where the logs from Argo CD were aggregated - could have potentially obtained the credentials to the Helm OCI repository.

If you are using Helm OCI repositories with Argo CD, it is strongly recommended to upgrade Argo CD to the latest patch version and to change the credentials used to access the repositories.

### Patches

A patch for this vulnerability is available with the v1.8.7 and v1.7.14 releases of Argo CD.

### Workarounds

No workaround available

### References

N/A

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel `#argo-cd`

### Credits

This vulnerability was found and reported by a third-party who wishes to stay anonymous. We want to thank this third-party for disclosing this vulnerability to us in a responsible manner.

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-6w87-g839-9wv7
- https://github.com/argoproj/argo-cd
