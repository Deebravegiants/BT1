# [M] containerd CRI stream server vulnerable to host memory exhaustion via terminal

## Summary
Severity: Medium
Advisory: GHSA-2qjp-425j-52j9
CVE: CVE-2022-23471
CWE: CWE-400, CWE-401
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-07
Source: https://github.com/advisories/GHSA-2qjp-425j-52j9
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.5.16
- Go: `github.com/containerd/containerd` — affected >=1.6.0 <1.6.12

## Details
### Impact

A bug was found in containerd's CRI implementation where a user can exhaust memory on the host. In the CRI stream server, a goroutine is launched to handle terminal resize events if a TTY is requested. If the user's process fails to launch due to, for example, a faulty command, the goroutine will be stuck waiting to send without a receiver, resulting in a memory leak. Kubernetes and crictl can both be configured to use containerd's CRI implementation and the stream server is used for handling container IO.

### Patches

This bug has been fixed in containerd 1.6.12 and 1.5.16.  Users should update to these versions to resolve the issue.

### Workarounds

Ensure that only trusted images and commands are used and that only trusted users have permissions to execute commands in running containers. 

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-2qjp-425j-52j9
- https://nvd.nist.gov/vuln/detail/CVE-2022-23471
- https://github.com/containerd/containerd/commit/241563be06a3de8b6a849414c4e805b68d3bb295
- https://github.com/containerd/containerd/commit/a05d175400b1145e5e6a735a6710579d181e7fb0
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/releases/tag/v1.5.16
- https://github.com/containerd/containerd/releases/tag/v1.6.12
- https://security.gentoo.org/glsa/202401-31
