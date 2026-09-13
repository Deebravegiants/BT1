# [C] Argo CD cluster secret might leak in cluster details page

## Summary
Severity: Critical
Advisory: GHSA-fwr2-64vr-xv9m
CVE: CVE-2023-40029
CWE: CWE-200, CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-09-11
Source: https://github.com/advisories/GHSA-fwr2-64vr-xv9m
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.2.0 <2.6.15
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.7.0 <2.7.14
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.8.0 <2.8.3

## Details
### Impact

Argo CD Cluster secrets might be managed declaratively using Argo CD / kubectl apply. As a result, the full secret body is stored in`kubectl.kubernetes.io/last-applied-configuration` annotation. 

https://github.com/argoproj/argo-cd/pull/7139 introduced the ability to manage cluster labels and annotations. Since clusters are stored as secrets it also exposes the `kubectl.kubernetes.io/last-applied-configuration` annotation which includes full secret body. In order to view the cluster annotations via the Argo CD API, the user must have `clusters, get` RBAC access.

**Note:** In many cases, cluster secrets do not contain any actually-secret information. But sometimes, as in bearer-token auth, the contents might be very sensitive.

### Patches

The bug has been patched in the following versions:

* 2.8.3
* 2.7.14
* 2.6.15

### Workarounds

Update/Deploy cluster secret with `server-side-apply` flag which does not use or rely on `kubectl.kubernetes.io/last-applied-configuration` annotation. Note: annotation for existing secrets will require manual removal.

### For more information

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-fwr2-64vr-xv9m
- https://nvd.nist.gov/vuln/detail/CVE-2023-40029
- https://github.com/argoproj/argo-cd/pull/7139
- https://github.com/argoproj/argo-cd/commit/44e52c4ae76e6da1343bdd54e57a822d93549f28
- https://github.com/argoproj/argo-cd/commit/4b2e5b06bff2ffd8ed1970654ddd8e55fc4a41c4
- https://github.com/argoproj/argo-cd/commit/7122b83fc346ec2729227405a2f9c2aa84b0bf80
- https://github.com/argoproj/argo-cd
- https://github.com/argoproj/argo-cd/releases/tag/v2.6.15
- https://github.com/argoproj/argo-cd/releases/tag/v2.7.14
- https://github.com/argoproj/argo-cd/releases/tag/v2.8.3
