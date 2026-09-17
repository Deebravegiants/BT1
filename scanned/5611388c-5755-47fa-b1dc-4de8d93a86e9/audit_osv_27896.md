# [H] afs: Increase buffer size in afs_update_volume_status()

## Summary
Severity: High
Advisory: CVE-2024-26736
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26736
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.270, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Increase buffer size in afs_update_volume_status()

The max length of volume->vid value is 20 characters.
So increase idbuf[] size up to 24 to avoid overflow.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

[DH: Actually, it's 20 + NUL, so increase it to 24 and use snprintf()]

## References
- https://git.kernel.org/stable/c/5c27d85a69fa16a08813ba37ddfb4bbc9a1ed6b5
- https://git.kernel.org/stable/c/6e6065dd25b661420fac19c34282b6c626fcd35e
- https://git.kernel.org/stable/c/6ea38e2aeb72349cad50e38899b0ba6fbcb2af3d
- https://git.kernel.org/stable/c/d34a5e57632bb5ff825196ddd9a48ca403626dfa
- https://git.kernel.org/stable/c/d9b5e2b7a8196850383c70d099bfd39e81ab6637
- https://git.kernel.org/stable/c/e56662160fc24d28cb75ac095cc6415ae1bda43e
- https://git.kernel.org/stable/c/e8530b170e464017203e3b8c6c49af6e916aece1
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26736.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26736
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
