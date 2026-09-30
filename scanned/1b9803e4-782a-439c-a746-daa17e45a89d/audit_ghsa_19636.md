# [M] containerd has an integer overflow in User ID handling

## Summary
Severity: Medium
Advisory: GHSA-265r-hfxg-fhmg
CVE: CVE-2024-40635
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-17
Source: https://github.com/advisories/GHSA-265r-hfxg-fhmg
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd/v2` — affected >=0 <2.0.4
- Go: `github.com/containerd/containerd` — affected >=1.7.0-beta.0 <1.7.27
- Go: `github.com/containerd/containerd` — affected >=0 <1.6.38

## Details
### Impact
A bug was found in containerd where containers launched with a User set as a `UID:GID` larger than the maximum 32-bit signed integer can cause an overflow condition where the container ultimately runs as root (UID 0). This could cause unexpected behavior for environments that require containers to run as a non-root user.

### Patches
This bug has been fixed in the following containerd versions: 

* 2.0.4 (Fixed in https://github.com/containerd/containerd/commit/1a43cb6a1035441f9aca8f5666a9b3ef9e70ab20)
* 1.7.27 (Fixed in https://github.com/containerd/containerd/commit/05044ec0a9a75232cad458027ca83437aae3f4da)
* 1.6.38 (Fixed in https://github.com/containerd/containerd/commit/cf158e884cfe4812a6c371b59e4ea9bc4c46e51a)

Users should update to these versions to resolve the issue.

### Workarounds
Ensure that only trusted images are used and that only trusted users have permissions to import images.

### Credits
The containerd project would like to thank [Benjamin Koltermann](https://github.com/p4ck3t0) and [emxll](https://github.com/emxll) for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### References
* https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-40635

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-265r-hfxg-fhmg
- https://nvd.nist.gov/vuln/detail/CVE-2024-40635
- https://github.com/containerd/containerd/commit/05044ec0a9a75232cad458027ca83437aae3f4da
- https://github.com/containerd/containerd/commit/1a43cb6a1035441f9aca8f5666a9b3ef9e70ab20
- https://github.com/containerd/containerd/commit/cf158e884cfe4812a6c371b59e4ea9bc4c46e51a
- https://github.com/containerd/containerd
- https://lists.debian.org/debian-lts-announce/2025/05/msg00005.html
