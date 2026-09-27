# [M] containerd: CRI checkpoint import allows local image tag poisoning

## Summary
Severity: Medium
Advisory: GHSA-cvxm-645q-p574
CVE: CVE-2026-50195
CWE: CWE-345, CWE-829
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-cvxm-645q-p574
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0 <2.1.9
- Go: `github.com/containerd/containerd/v2` — affected >=2.2.0 <2.2.5
- Go: `github.com/containerd/containerd/v2` — affected >=2.3.0 <2.3.2

## Details
## Impact
containerd's CRI checkpoint import process contains a vulnerability where it fails to validate the image references specified within a checkpoint image's configuration. An attacker with permissions to create pods can use a crafted checkpoint image to force containerd to pull a malicious image and assign it an arbitrary local tag, thereby poisoning the node's local image cache. Subsequently, if other pods on the same node attempt to use the poisoned tag with an `IfNotPresent` (or `Never`) pull policy, they will unknowingly execute the attacker's malicious image instead of the legitimate one. This can lead to a compromise of the affected pods, allowing the attacker to execute arbitrary code under the victim pod's identity.

## Patches
This bug has been fixed in the following containerd versions:

* 2.3.2
* 2.2.5
* 2.1.9

Users should update to these versions to resolve the issue.
## Workarounds
Users should only allow trusted images to be pulled.

## Credits
The containerd project would like to thank Henry Beberman (@hbeberman) of Microsoft, the GKE Security Team using Gemini, Anthropic Research, in collaboration with Claude, and Robert Prast (@robertprast) who independently discovered and responsibly disclosed this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

## For more information
If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-cvxm-645q-p574
- https://nvd.nist.gov/vuln/detail/CVE-2026-50195
- https://github.com/containerd/containerd
