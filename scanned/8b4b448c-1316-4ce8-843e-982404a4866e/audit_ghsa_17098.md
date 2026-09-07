# [M] Users with `create` but not `override` privileges can perform local sync

## Summary
Severity: Medium
Advisory: GHSA-g623-jcgg-mhmm
CVE: CVE-2023-50726
CWE: CWE-269, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-g623-jcgg-mhmm
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=1.2.0-rc1
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.9.0 <2.9.8
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.10.0 <2.10.3
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.0.0-rc3 <2.8.12

## Details
### Impact

"Local sync" is an Argo CD feature that allows developers to temporarily override an Application's manifests with locally-defined manifests. Use of the feature should generally be limited to highly-trusted users, since it allows the user to bypass any merge protections in git.

An improper validation bug allows users who have `create` privileges but not `override` privileges to sync local manifests on app creation. All other restrictions, including AppProject restrictions are still enforced. The only restriction which is _not_ enforced is that the manifests come from some approved git/Helm/OCI source.

The bug was introduced in 1.2.0-rc1 when the local manifest sync feature was added.

### Patches

The bug has been patched in the following versions:

* 2.10.3
* 2.9.8
* 2.8.12

### Workarounds

To immediately mitigate the risk of branch protection bypass, remove `applications, create` RBAC access. The only way to eliminate the issue without removing RBAC access is to upgrade to a patched version.

Branch protection rules and review requirements are a great way to enforce security constraints in a GitOps environment, but they should be just one layer in a multi-layered approach. Make sure your AppProject and RBAC restrictions are as thorough as possible to prevent a review bypass vulnerability from permitting excessive damage.

### References

* [Argo CD RBAC documentation](https://argo-cd.readthedocs.io/en/latest/operator-manual/rbac/)

### For more information

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-g623-jcgg-mhmm
- https://nvd.nist.gov/vuln/detail/CVE-2023-50726
- https://github.com/argoproj/argo-cd/commit/3b8f673f06c2d228e01cbc830e5cb57cef008978
- https://argo-cd.readthedocs.io/en/latest/operator-manual/rbac
- https://github.com/argoproj/argo-cd
