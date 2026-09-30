# [M] containerd environment variable leak

## Summary
Severity: Medium
Advisory: GHSA-6g2q-w5j3-fwh4
CVE: CVE-2021-21334
CWE: CWE-200, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-6g2q-w5j3-fwh4
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=1.4.0 <1.4.4
- Go: `github.com/containerd/containerd` — affected >=0 <1.3.10

## Details
## Impact

Containers launched through containerd's CRI implementation (through Kubernetes, crictl, or any other pod/container client that uses the containerd CRI service) that share the same image may receive incorrect environment variables, including values that are defined for other containers.  If the affected containers have different security contexts, this may allow sensitive information to be unintentionally shared.

If you are not using containerd’s CRI implementation (through one of the mechanisms described above), you are not vulnerable to this issue.

If you are not launching multiple containers or Kubernetes pods from the same image which have different environment variables, you are not vulnerable to this issue.

If you are not launching multiple containers or Kubernetes pods from the same image in rapid succession, you have reduced likelihood of being vulnerable to this issue

## Patches

This vulnerability has been fixed in containerd 1.3.10 and containerd 1.4.4.  Users should update to these versions as soon as they are released.

## Workarounds

There are no known workarounds.

## For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/containerd/containerd/issues/new/choose)
* Email us at security@containerd.io if you think you’ve found a security bug.

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-6g2q-w5j3-fwh4
- https://nvd.nist.gov/vuln/detail/CVE-2021-21334
- https://github.com/containerd/cri/pull/1628
- https://github.com/containerd/cri/pull/1629
- https://github.com/containerd/containerd/commit/05f951a3781f4f2c1911b05e61c160e9c30eaa8e
- https://github.com/containerd/containerd/commit/2d9c8aa4b3f4313982c5c999af57212a1c5d144b
- https://github.com/containerd/containerd/commit/cbcb2f57fbe221986f96b552855eb802f63193de
- https://github.com/containerd/containerd/releases/tag/v1.3.10
- https://github.com/containerd/containerd/releases/tag/v1.4.4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KUE2Z2ZUWBHRU36ZGBD2YSJCYB6ELPXE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QIBPKSX5IOWPM3ZPFB3JVLXWDHSZTTWT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VTXHA5JOWQRCCUZH7ZQBEYN6KZKJEYSD
- https://security.gentoo.org/glsa/202105-33
