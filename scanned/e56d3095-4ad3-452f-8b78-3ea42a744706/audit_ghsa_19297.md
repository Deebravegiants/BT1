# [M] containerd CRI plugin: Incorrect cgroup hierarchy assignment for containers running in usernamespaced Kubernetes pods.

## Summary
Severity: Medium
Advisory: GHSA-cxfp-7pvr-95ff
CVE: CVE-2025-47291
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-cxfp-7pvr-95ff
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd/v2` — affected >=2.0.1 <2.0.5

## Details
# Impact

A bug was found in the containerd's CRI implementation where containerd doesn't put usernamespaced containers under the Kubernetes' cgroup hierarchy, therefore some Kubernetes limits are not honored. This may cause a denial of service of the Kubernetes node.

# Patches

This bug has been fixed in containerd 2.0.5+ and 2.1.0+. Users should update to these versions to resolve the issue.

# Workarounds

Disable usernamespaced pods in Kubernetes temporarily.

# Credits

The containerd project would like to thank Rodrigo Campos Catelin and Piotr Rogowski for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

#  For more information
If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at security@containerd.io

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-cxfp-7pvr-95ff
- https://nvd.nist.gov/vuln/detail/CVE-2025-47291
- https://github.com/containerd/containerd
- https://pkg.go.dev/vuln/GO-2025-3701
