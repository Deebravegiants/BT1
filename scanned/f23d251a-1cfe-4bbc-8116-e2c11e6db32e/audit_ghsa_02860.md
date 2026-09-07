# [M] Insufficiently restricted permissions on plugin directories

## Summary
Severity: Medium
Advisory: GHSA-c2h3-6mxw-7mvq
CVE: CVE-2021-41103
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-10-04
Source: https://github.com/advisories/GHSA-c2h3-6mxw-7mvq
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.4.11
- Go: `github.com/containerd/containerd` — affected >=1.5.0 <1.5.7

## Details
### Impact
A bug was found in containerd where container root directories and some plugins had insufficiently restricted permissions, allowing otherwise unprivileged Linux users to traverse directory contents and execute programs. When containers included executable programs with extended permission bits (such as setuid), unprivileged Linux users could discover and execute those programs. When the UID of an unprivileged Linux user on the host collided with the file owner or group inside a container, the unprivileged Linux user on the host could discover, read, and modify those files.

### Patches
This vulnerability has been fixed in containerd 1.4.11 and containerd 1.5.7. Users should update to these version when they are released and may restart containers or update directory permissions to mitigate the vulnerability.

### Workarounds
Limit access to the host to trusted users. Update directory permission on container bundles directories. 

### For more information
If you have any questions or comments about this advisory: 
* Open an issue in [github.com/containerd/containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-c2h3-6mxw-7mvq
- https://nvd.nist.gov/vuln/detail/CVE-2021-41103
- https://github.com/containerd/containerd/commit/5b46e404f6b9f661a205e28d59c982d3634148f8
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/releases/tag/v1.4.11
- https://github.com/containerd/containerd/releases/tag/v1.5.7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B5Q6G6I4W5COQE25QMC7FJY3I3PAYFBB
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZNFADTCHHYWVM6W4NJ6CB4FNFM2VMBIB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B5Q6G6I4W5COQE25QMC7FJY3I3PAYFBB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZNFADTCHHYWVM6W4NJ6CB4FNFM2VMBIB
- https://security.gentoo.org/glsa/202401-31
- https://www.debian.org/security/2021/dsa-5002
