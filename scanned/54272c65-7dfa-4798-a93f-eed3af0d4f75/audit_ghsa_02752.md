# [M] Archive package allows chmod of file outside of unpack target directory

## Summary
Severity: Medium
Advisory: GHSA-c72p-9xmj-rx3w
CVE: CVE-2021-32760
CWE: CWE-668, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-c72p-9xmj-rx3w
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.4.8
- Go: `github.com/containerd/containerd` — affected >=1.5.0 <1.5.4

## Details
## Impact

A bug was found in containerd where pulling and extracting a specially-crafted container image can result in Unix file permission changes for existing files in the host’s filesystem.  Changes to file permissions can deny access to the expected owner of the file, widen access to others, or set extended bits like setuid, setgid, and sticky.  This bug does not directly allow files to be read, modified, or executed without an additional cooperating process.

## Patches

This bug has been fixed in containerd 1.5.4 and 1.4.8.  Users should update to these versions as soon as they are released.  Running containers do not need to be restarted.

## Workarounds

Ensure you only pull images from trusted sources.

Linux security modules (LSMs) like SELinux and AppArmor can limit the files potentially affected by this bug through policies and profiles that prevent containerd from interacting with unexpected files.

## For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/containerd/containerd/issues/new/choose)
* Email us at security@containerd.io if you think you’ve found a security bug.

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-c72p-9xmj-rx3w
- https://nvd.nist.gov/vuln/detail/CVE-2021-32760
- https://github.com/containerd/containerd/commit/22e9a70c71eff6507be71955947a611f2ed91e6c
- https://github.com/containerd/containerd/commit/7ad08c69e09ee4930a48dbf2aab3cd612458617f
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/releases/tag/v1.4.8
- https://github.com/containerd/containerd/releases/tag/v1.5.4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DDMNDPJJTP3J5GOEDB66F6MGXUTRG3Y3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DDMNDPJJTP3J5GOEDB66F6MGXUTRG3Y3
- https://security.gentoo.org/glsa/202401-31
