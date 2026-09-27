# [M] containerd image-triggered runtime DoS via unbounded group parsing

## Summary
Severity: Medium
Advisory: GHSA-jpcc-p29g-p8mq
CVE: CVE-2026-47262
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-jpcc-p29g-p8mq
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd/v2` — affected >=2.0.0 <2.0.10
- Go: `github.com/containerd/containerd` — affected >=1.7.0 <1.7.33
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0 <2.1.9
- Go: `github.com/containerd/containerd/v2` — affected >=2.2.0 <2.2.5
- Go: `github.com/containerd/containerd/v2` — affected >=2.3.0 <2.3.2

## Details
### Impact
A vulnerability in containerd allows a maliciously crafted image to cause a Denial of Service (DoS) condition. When creating a container from this image, memory exhaustion occurs, leading to an Out Of Memory (OOM) kill of the containerd process. This renders the container runtime API unavailable and can disrupt clients such as the Docker Engine or Kubernetes control-plane components.

### Patches
This bug has been fixed in the following containerd versions:

* 2.3.2
* 2.2.5
* 2.1.9
* 2.0.10
* 1.7.33

Users should update to these versions to resolve the issue.

### Workarounds
Ensure that only trusted images are used and that only trusted users have permissions to import images or schedule pods. 

### Credits

The containerd project would like to thank Jakub Ciolek (@jake-ciolek) at AlphaSense and Kyle Elliott @ Trail of Bits who independently discovered and responsibly disclosed this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-jpcc-p29g-p8mq
- https://github.com/containerd/containerd
