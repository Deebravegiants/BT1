# [H] Podman vulnerable to memory-based denial of service

## Summary
Severity: High
Advisory: GHSA-rpcc-p8xm-rc6p
CVE: CVE-2024-3056
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-02
Source: https://github.com/advisories/GHSA-rpcc-p8xm-rc6p
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v5` — affected >=0
- Go: `github.com/containers/podman` — affected >=0
- Go: `github.com/containers/podman/v2` — affected >=0
- Go: `github.com/containers/podman/v3` — affected >=0
- Go: `github.com/containers/podman/v4` — affected >=0

## Details
A flaw was found in Podman. This issue may allow an attacker to create a specially crafted container that, when configured to share the same IPC with at least one other container, can create a large number of IPC resources in /dev/shm. The malicious container will continue to exhaust resources until it is out-of-memory (OOM) killed. While the malicious container's cgroup will be removed, the IPC resources it created are not. Those resources are tied to the IPC namespace that will not be removed until all containers using it are stopped, and one non-malicious container is holding the namespace open. The malicious container is restarted, either automatically or by attacker control, repeating the process and increasing the amount of memory consumed. With a container configured to restart always, such as `podman run --restart=always`, this can result in a memory-based denial of service of the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3056
- https://access.redhat.com/security/cve/CVE-2024-3056
- https://bugzilla.redhat.com/show_bug.cgi?id=2270717
- https://github.com/containers/podman
- https://pkg.go.dev/vuln/GO-2024-3042
- https://security.netapp.com/advisory/ntap-20241227-0002
