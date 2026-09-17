# [H] containerd CRI checkpoint restore CDI annotation smuggling

## Summary
Severity: High
Advisory: GHSA-33vj-92qq-66hc
CVE: CVE-2026-53492
CWE: CWE-20, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-33vj-92qq-66hc
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0 <2.1.9
- Go: `github.com/containerd/containerd/v2` — affected >=2.2.0 <2.2.5
- Go: `github.com/containerd/containerd/v2` — affected >=2.3.0 <2.3.2

## Details
### Impact

containerd's CRI implementation improperly trusts Container Device Interface (CDI) annotations found within untrusted checkpoint image metadata during container restoration. When restoring a container from a checkpoint, containerd preserves CDI-related annotations from the checkpoint archive rather than relying solely on the pod's create-time specification. This allows a user with pod creation permissions to bypass standard Kubernetes resource allocation and device plugin enforcement, injecting arbitrary CDI edits (such as device nodes and host mounts) into the restored container. Successful exploitation requires that the node has CDI enabled and contains a matching host CDI specification for the requested device; environments where CDI is disabled or lacking sensitive device specifications are not affected.

### Patches

This bug has been fixed in the following containerd versions:

* 2.3.2
* 2.2.5
* 2.1.9

Users should update to these versions to resolve the issue. Recreating existing containers restored from untrusted checkpoints may be necessary to remove smuggled configuration.

### Workarounds

Users can mitigate this issue by restricting the restoration of containers from untrusted checkpoint images. If Container Device Interface (CDI) capabilities are not utilized on the node, removing or temporarily relocating host CDI specifications from the default directories (`/etc/cdi` and `/var/run/cdi`) will eliminate the reachability of this vulnerability.

### Credits

The containerd project would like to thank Robert Prast (@robertprast) for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-33vj-92qq-66hc
- https://github.com/containerd/containerd
