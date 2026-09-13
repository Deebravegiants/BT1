# [M] Buildah processes using chroot isolation may leak environment values to intermediate processes

## Summary
Severity: Medium
Advisory: GHSA-7638-r9r3-rmjj
CVE: CVE-2021-3602
CWE: CWE-200, CWE-212
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-07-19
Source: https://github.com/advisories/GHSA-7638-r9r3-rmjj
Type: github-advisory

## Affected
- Go: `github.com/containers/buildah` — affected >=0 <1.16.8
- Go: `github.com/containers/buildah` — affected >=1.17.0 <1.17.2
- Go: `github.com/containers/buildah` — affected >=1.18.0 <1.19.9
- Go: `github.com/containers/buildah` — affected >=1.20.0 <1.21.3

## Details
### Impact
When running processes using "chroot" isolation, the process being run can examine the environment variables of its immediate parent and grandparent processes (CVE-2021-3602).  This isolation type is often used when running `buildah` in unprivileged containers, and it is often used to do so in CI/CD environments.  If sensitive information is exposed to the original `buildah` process through its environment, that information will unintentionally be shared with child processes which it starts as part of handling RUN instructions or during `buildah run`.  The commands that `buildah` is instructed to run can read that information if they choose to.

### Patches
Users should upgrade packages, or images which contain packages, to include version 1.21.3 or later.

### Workarounds
As a workaround, invoking `buildah` in a container under `env -i` to have it started with a reinitialized environment should prevent the leakage.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [buildah](https://github.com/containers/buildah/issues)
* Email us at [the buildah general mailing list](mailto:buildah@lists.buildah.io), or [the podman security mailing list](mailto:security@lists.podman.io) if it's sensitive.

## References
- https://github.com/containers/buildah/security/advisories/GHSA-7638-r9r3-rmjj
- https://nvd.nist.gov/vuln/detail/CVE-2021-3602
- https://github.com/containers/buildah/commit/a468ce0ffd347035d53ee0e26c205ef604097fb0
- https://bugzilla.redhat.com/show_bug.cgi?id=1969264
- https://github.com/containers/buildah
- https://pkg.go.dev/vuln/GO-2022-0345
- https://ubuntu.com/security/CVE-2021-3602
