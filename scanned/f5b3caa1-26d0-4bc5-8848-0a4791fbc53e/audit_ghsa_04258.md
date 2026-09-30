# [H] containerd CRI — image-config `LABEL` flows to restart-monitor `binary://` logger: host-root command execution from an image pull

## Summary
Severity: High
Advisory: GHSA-xhf5-7wjv-pqxp
CVE: CVE-2026-53488
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-xhf5-7wjv-pqxp
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=1.7.0 <1.7.33
- Go: `github.com/containerd/containerd/v2` — affected >=2.0.0 <2.0.10
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0 <2.1.9
- Go: `github.com/containerd/containerd/v2` — affected >=2.2.0 <2.2.5
- Go: `github.com/containerd/containerd/v2` — affected >=2.3.0 <2.3.2

## Details
### Impact
A bug was found in containerd where the CRI plugin propagates labels from an image config (`LABEL` instruction in Dockerfile) to a container without validation. This may result in executing an arbitrary command on the host, via a plugin that consumes container labels for some operations.

### Patches
This bug has been fixed in the following containerd versions:

* 2.3.2
* 2.2.5
* 2.1.9
* 2.0.10
* 1.7.33

Users should update to these versions to resolve the issue.

### Workarounds
Ensure that only trusted images are used.

### Credits
The containerd project would like to thank Anthropic Research, in collaboration with Claude, the GKE Security Team using Gemini, and Robert Prast (@robertprast) for independently discovering and responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-xhf5-7wjv-pqxp
- https://github.com/containerd/containerd
