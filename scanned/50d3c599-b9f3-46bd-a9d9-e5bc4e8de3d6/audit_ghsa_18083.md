# [H] Youki: If /proc and /sys in the rootfs are symbolic links, they can potentially be exploited to gain access to the host root filesystem.

## Summary
Severity: High
Advisory: GHSA-j26p-6wx7-f3pw
CVE: CVE-2025-54867
CWE: CWE-61
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-14
Source: https://github.com/advisories/GHSA-j26p-6wx7-f3pw
Type: github-advisory

## Affected
- crates.io: `youki` — affected >=0 <0.5.5

## Details
### Summary
If `/proc` and `/sys` in the rootfs are symbolic links, they can potentially be exploited to gain access to the host root filesystem.

### Details

For security reasons, container creation should be prohibited if `/proc` or `/sys` in the rootfs is a symbolic link.
I verified this behavior with `youki`.
When `/proc` or `/sys` is a symbolic link, `runc` fails to create the container, whereas `youki` successfully creates it.

This is the fix related to this issue in `runc`.
* https://github.com/opencontainers/runc/pull/3756
* https://github.com/opencontainers/runc/pull/3773
* https://github.com/opencontainers/runc/blob/main/libcontainer/rootfs_linux.go#L590
* https://github.com/opencontainers/runc/blob/main/tests/integration/mask.bats#L60


### Impact

The following advisory appears to be related to this vulnerability:
* https://github.com/advisories/GHSA-vpvm-3wq2-2wvm
* https://github.com/advisories/GHSA-fh74-hm69-rqjw

## References
- https://github.com/youki-dev/youki/security/advisories/GHSA-j26p-6wx7-f3pw
- https://nvd.nist.gov/vuln/detail/CVE-2025-54867
- https://github.com/youki-dev/youki/commit/0d9b4f2aa5ceaf988f3eb568711d2acf0a4ace37
- https://github.com/youki-dev/youki
- https://github.com/youki-dev/youki/releases/tag/v0.5.5
