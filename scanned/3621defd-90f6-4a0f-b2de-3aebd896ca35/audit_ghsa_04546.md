# [H] Arbitrary host CRI log file read via symlink following in CRI checkpoint restore

## Summary
Severity: High
Advisory: GHSA-rgh6-rfwx-v388
CVE: CVE-2026-53489
CWE: CWE-61
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-rgh6-rfwx-v388
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0 <2.1.9
- Go: `github.com/containerd/containerd/v2` — affected >=2.2.0 <2.2.5
- Go: `github.com/containerd/containerd/v2` — affected >=2.3.0 <2.3.2

## Details
### Impact
A bug was found in containerd where the CRI plugin restores `container.log` from a checkpoint image without validating a symlinked path. This could result in reading an arbitrary file on the host via `kubectl logs`.

### Patches
This bug has been fixed in the following containerd versions:

* 2.3.2
* 2.2.5
* 2.1.9

Users should update to these versions to resolve the issue.

### Workarounds
Ensure that only trusted images and checkpoints are used.

### Credits
The containerd project would like to thank @gouldnicholas and @davidrxchester, Yuming Zhang and Song Li of Zhejiang University, Sangwon Ryu (@sangwon090), Henry Beberman (@hbeberman) of Microsoft, the GKE Security Team using Gemini, Anthropic Research, in collaboration with Claude, Robert Prast (@robertprast),
Kyle Elliott (@kyle-elliott-tob) of Trail of Bits, and Zhenchen Wang (@Plucky923), who independently discovered and responsibly disclosed this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-rgh6-rfwx-v388
- https://github.com/containerd/containerd
