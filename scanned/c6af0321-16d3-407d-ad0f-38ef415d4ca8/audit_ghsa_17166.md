# [M] ArgoCD's repo server has Uncontrolled Resource Consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jhwx-mhww-rgc3
CVE: CVE-2024-29893
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-jhwx-mhww-rgc3
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.4.0 <2.8.14
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.9.0 <2.9.10
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.10.0 <2.10.5

## Details
### Impact
All versions of ArgoCD starting from v2.4 have a bug where the ArgoCD repo-server component is vulnerable to a Denial-of-Service attack vector. Specifically,  it's possible to crash the repo server component through an out of memory error by pointing it to a malicious Helm registry.
The loadRepoIndex() function in the ArgoCD's helm package, does not limit the size nor time while fetching the data. It fetches it and creates a byte slice from the retrieved data in one go. If the registry is implemented to push data continuously, the repo server will keep allocating memory until it runs out of it.

### Patches
A patch for this vulnerability has been released in the following Argo CD versions:

v2.10.5
v2.9.10
v2.8.14

### For more information
If you have any questions or comments about this advisory:

Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd


### Credits
This vulnerability was found & reported by Jakub Ciolek

The Argo team would like to thank these contributors for their responsible disclosure and constructive communications during the resolve of this issue

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-jhwx-mhww-rgc3
- https://nvd.nist.gov/vuln/detail/CVE-2024-29893
- https://github.com/argoproj/argo-cd/commit/14f681e3ee7c38731943b98f92277e88a3db109d
- https://github.com/argoproj/argo-cd/commit/36b8a12a38f8d92d55bffc81deed44389bf6eb59
- https://github.com/argoproj/argo-cd/commit/3e5a878f6e30d935fa149723ea2a2e93748fcddd
- https://github.com/argoproj/argo-cd
