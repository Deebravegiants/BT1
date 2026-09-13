# [H] Path traversal and files overwrite with unsquashfs in singularity

## Summary
Severity: High
Advisory: GHSA-7gcp-w6ww-2xv9
CVE: CVE-2020-15229
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-7gcp-w6ww-2xv9
Type: github-advisory

## Affected
- Go: `github.com/sylabs/singularity` — affected >=3.1.1 <3.6.4

## Details
### Impact

Due to insecure handling of path traversal and the lack of path sanitization within `unsquashfs` (a distribution provided utility used by Singularity), it is possible to overwrite/create any files on the host filesystem during the extraction of a crafted squashfs filesystem.

Squashfs extraction occurs automatically for unprivileged execution of Singularity (either `--without-suid` installation or with `allow setuid = no`) when a user attempts to run an image which:

- is a local SIF image or a single file containing a squashfs filesystem
- is pulled from remote sources `library://` or `shub://`

Image build is also impacted in a more serious way as it is often performed by the root user, allowing an attacker to overwrite/create files leading to a system compromise.  Bootstrap methods `library`, `shub` and `localimage` trigger a squashfs extraction.

### Patches

This issue is addressed in Singularity 3.6.4.

All users are advised to upgrade to 3.6.4 especially if they use Singularity mainly for building image as root user.

### Workarounds

There is no solid workaround except to temporarily avoid use of unprivileged mode with single file images, in favor of sandbox images instead. Regarding image build, temporarily avoid building from `library` and `shub` sources, and as much as possible use `--fakeroot` or a VM to limit potential impact.

### For more information

General questions about the impact of the advisory / changes made in the 3.6.0 release can be asked in the:

* [Singularity Slack Channel](https://bit.ly/2m0g3lX)
* [Singularity Mailing List](https://groups.google.com/a/lbl.gov/forum/??sdf%7Csort:date#!forum/singularity)

Any sensitive security concerns should be directed to: security@sylabs.io

See our Security Policy here: https://sylabs.io/security-policy

## References
- https://github.com/hpcng/singularity/security/advisories/GHSA-7gcp-w6ww-2xv9
- https://nvd.nist.gov/vuln/detail/CVE-2020-15229
- https://github.com/hpcng/singularity/pull/5611
- https://github.com/hpcng/singularity/commit/eba3dea260b117198fdb6faf41f2482ab2f8d53e
- https://github.com/hpcng/singularity/blob/v3.6.4/CHANGELOG.md#security-related-fixes
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00070.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00071.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00009.html
