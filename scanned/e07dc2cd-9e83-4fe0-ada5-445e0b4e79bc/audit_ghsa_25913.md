# [H] containerd CRI plugin: Insecure handling of image volumes

## Summary
Severity: High
Advisory: GHSA-crp2-qrr5-8pq7
CVE: CVE-2022-23648
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-02
Source: https://github.com/advisories/GHSA-crp2-qrr5-8pq7
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.4.13
- Go: `github.com/containerd/containerd` — affected >=1.5.0 <1.5.10
- Go: `github.com/containerd/containerd` — affected >=1.6.0 <1.6.1

## Details
### Impact

A bug was found in containerd where containers launched through containerd’s CRI implementation with a specially-crafted image configuration could gain access to read-only copies of arbitrary files and directories on the host.  This may bypass any policy-based enforcement on container setup (including a Kubernetes Pod Security Policy) and expose potentially sensitive information.  Kubernetes and crictl can both be configured to use containerd’s CRI implementation.

### Patches

This bug has been fixed in containerd 1.6.1, 1.5.10 and 1.4.13.  Users should update to these versions to resolve the issue.

### Workarounds

Ensure that only trusted images are used.

### Credits

The containerd project would like to thank Felix Wilhelm of Google Project Zero for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-crp2-qrr5-8pq7
- https://nvd.nist.gov/vuln/detail/CVE-2022-23648
- https://github.com/containerd/containerd/commit/10f428dac7cec44c864e1b830a4623af27a9fc70
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/releases/tag/v1.4.13
- https://github.com/containerd/containerd/releases/tag/v1.5.10
- https://github.com/containerd/containerd/releases/tag/v1.6.1
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AUDQUQBZJGBWJPMRVB6QCCCRF7O3O4PA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HFTS2EF3S7HNYSNZSEJZIJHPRU7OPUV3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OCCARJ6FU4MWBTXHZNMS7NELPDBIX2VO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AUDQUQBZJGBWJPMRVB6QCCCRF7O3O4PA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HFTS2EF3S7HNYSNZSEJZIJHPRU7OPUV3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OCCARJ6FU4MWBTXHZNMS7NELPDBIX2VO
- https://security.gentoo.org/glsa/202401-31
- https://www.debian.org/security/2022/dsa-5091
- http://packetstormsecurity.com/files/166421/containerd-Image-Volume-Insecure-Handling.html
