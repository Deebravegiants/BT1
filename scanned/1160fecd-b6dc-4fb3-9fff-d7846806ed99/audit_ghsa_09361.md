# [H] containerd user ID handling bypass allows runAsNonRoot evasion

## Summary
Severity: High
Advisory: GHSA-fqw6-gf59-qr4w
CVE: CVE-2026-46680
CWE: CWE-269, CWE-843
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-fqw6-gf59-qr4w
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=1.7.27 <1.7.32
- Go: `github.com/containerd/containerd/v2` — affected >=2.0.4 <2.0.9
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0-beta.0 <2.2.4
- Go: `github.com/containerd/containerd/v2` — affected >=2.3.0-beta.0 <2.3.1

## Details
### Impact
A bug was found in containerd where containers launched with a numeric `User` directive that cannot be parsed as a 32-bit integer are incorrectly treated as a username. If a crafted image provides an `/etc/passwd` file mapping this large numeric string to root, the container ultimately runs as root (UID 0). This allows the Kubernetes `runAsNonRoot` restriction to be bypassed, causing unexpected behavior for environments that require containers to run as a non-root user.

### Patches
This bug has been fixed in the following containerd versions:

* 2.3.1
* 2.2.4
* 2.0.9
* 1.7.32

Note: The containerd 2.1 release has reached its [end of life](https://containerd.io/releases/#current-state-of-containerd-releases) and a fixed version is not provided.

Users should update to these versions to resolve the issue.

### Workarounds
Ensure that only trusted images are used and that only trusted users have permissions to import images. Alternatively, enforcing a specific numeric `runAsUser` in the Kubernetes Pod `securityContext` overrides the `USER` directive in the image and prevents the bypass. Newer versions of Kubernetes, starting with 1.34, also appear to enforce `runAsNonRoot` properly regardless of this bug.

### Credits
The containerd project would like to thank Lei Wang (@ssst0n3) for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### Resources
* https://github.com/advisories/GHSA-265r-hfxg-fhmg (CVE-2024-40635)

### For more information

If there are any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Send an email to [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Send an email to [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-fqw6-gf59-qr4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-46680
- https://github.com/containerd/containerd
