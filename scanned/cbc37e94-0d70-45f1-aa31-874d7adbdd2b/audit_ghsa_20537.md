# [H] Unprivileged pod using `hostPath` can side-step active LSM when it is SELinux

## Summary
Severity: High
Advisory: GHSA-mvff-h3cj-wj9c
CVE: CVE-2021-43816
CWE: CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-mvff-h3cj-wj9c
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=1.5.0 <1.5.9

## Details
### Impact

Containers launched through containerd’s CRI implementation on Linux systems which use the SELinux security module and containerd versions since v1.5.0 can cause arbitrary files and directories on the host to be relabeled to match the container process label through the use of specially-configured bind mounts in a hostPath volume. This relabeling elevates permissions for the container, granting full read/write access over the affected files and directories. Kubernetes and crictl can both be configured to use containerd’s CRI implementation.

If you are not using containerd’s CRI implementation (through one of the mechanisms described above), you are not affected by this issue.

### Patches

This bug has been fixed in containerd 1.5.9.  Because file labels persist independently of containerd, users should both update to these versions as soon as they are released and validate that all files on their host are correctly labeled.

### Workarounds

Ensure that no sensitive files or directories are used as a hostPath volume source location.  Policy enforcement mechanisms such a Kubernetes Pod Security Policy [AllowedHostPaths](https://kubernetes.io/docs/concepts/policy/pod-security-policy/#volumes-and-file-systems) may be specified to limit the files and directories that can be bind-mounted to containers.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-mvff-h3cj-wj9c
- https://nvd.nist.gov/vuln/detail/CVE-2021-43816
- https://github.com/containerd/containerd/issues/6194
- https://github.com/containerd/containerd/commit/a731039238c62be081eb8c31525b988415745eea
- https://github.com/dweomer/containerd/commit/f7f08f0e34fb97392b0d382e58916d6865100299
- https://github.com/containerd/containerd
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GD5GH7NMK5VJMA2Y5CYB5O5GTPYMWMLX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MPDIZMI7ZPERSZE2XO265UCK5IWM7CID
