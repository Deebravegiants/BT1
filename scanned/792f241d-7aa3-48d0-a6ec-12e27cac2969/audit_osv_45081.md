# [M] containerd: CRI ExecSync Goroutine Leak Leads to Node-Level Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-7jxh-36q5-gcqv
Aliases: CVE-2026-53495
Ecosystem: Go
Published: 2026-09-09
Source: https://osv.dev/vulnerability/GHSA-7jxh-36q5-gcqv
Type: osv

## Affected
- Go: `github.com/containerd/containerd/v2` — affected >=0 <2.0.12
- Go: `github.com/containerd/containerd` — affected >=0 <1.7.35
- Go: `github.com/containerd/containerd/v2` — affected >=2.2.0 <2.2.8
- Go: `github.com/containerd/containerd/v2` — affected >=2.3.0 <2.3.5

## Details
### Impact

A bug in containerd's CRI ExecSync implementation allows exec probes and lifecycle hooks with background child processes to keep containerd's stdio-drain goroutines indefinitely blocked. Because the I/O drain phase lacks a default timeout or context cancellation handling, repeated ExecSync invocations (like probes) that include long-lived background processes against a container can cause containerd to leak goroutines and host memory. Over time, this resource exhaustion can cause the containerd daemon to be terminated by the OOM killer, rendering containerd unavailable until it is restarted. This issue affects containerd on Linux systems running with the CRI plugin enabled. Users not using containerd's CRI implementation or not running containers on Linux are not affected.

### Patches

This bug has been fixed in containerd 2.3.5, 2.2.8, 2.0.12, and 1.7.35. Users should update to these versions to resolve the issue.

### Workarounds

Ensure exec probes and lifecycle hooks do not launch long-lived background child processes.

### Credits

The containerd project would like to thank XlabAI Team of Tencent Xuanwu Lab (xlabai@tencent.com), including Guannan Wang, Zhanpeng Liu, Jiashuo Liang, and Guancheng Li, and @IamwhatIamSY who independently discovered and responsibly disclosed this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### For more information

If there are any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Send an email to [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Send an email to [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-7jxh-36q5-gcqv
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/releases/tag/v1.7.35
- https://github.com/containerd/containerd/releases/tag/v2.0.12
- https://github.com/containerd/containerd/releases/tag/v2.2.8
- https://github.com/containerd/containerd/releases/tag/v2.3.5
