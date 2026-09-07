# [M] containerd CRI server: Host memory exhaustion through Attach goroutine leak

## Summary
Severity: Medium
Advisory: GHSA-m6hq-p25p-ffr2
CVE: CVE-2025-64329
CWE: CWE-401
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-06
Source: https://github.com/advisories/GHSA-m6hq-p25p-ffr2
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.7.29
- Go: `github.com/containerd/containerd/v2` — affected >=0 <2.0.7
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0-beta.0 <2.1.5
- Go: `github.com/containerd/containerd/v2` — affected >=2.2.0-beta.0 <2.2.0

## Details
### Impact

A bug was found in containerd's CRI Attach implementation where a user can exhaust memory on the host due to goroutine leaks. 

Repetitive calls of CRI Attach (e.g., [`kubectl attach`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_attach/)) could increase the memory usage of containerd.

### Patches

This bug has been fixed in the following containerd versions:

* 2.2.0
* 2.1.5
* 2.0.7
* 1.7.29

Users should update to these versions to resolve the issue.

### Workarounds

Set up an admission controller to control accesses to `pods/attach` resources.
e.g., [Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/).

### Credits

The containerd project would like to thank @Wheat2018 for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### References

https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-64329

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:

* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-m6hq-p25p-ffr2
- https://nvd.nist.gov/vuln/detail/CVE-2025-64329
- https://github.com/containerd/containerd/commit/083b53cd6f19b5de7717b0ce92c11bdf95e612df
- https://github.com/containerd/containerd
