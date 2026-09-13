# [H] block: Fix wrong offset in bio_truncate()

## Summary
Severity: High
Advisory: CVE-2022-48747
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48747
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.176, >=5.5.0 <5.15.19, >=5.11.0 <5.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: Fix wrong offset in bio_truncate()

bio_truncate() clears the buffer outside of last block of bdev, however
current bio_truncate() is using the wrong offset of page. So it can
return the uninitialized data.

This happened when both of truncated/corrupted FS and userspace (via
bdev) are trying to read the last of bdev.

## References
- https://git.kernel.org/stable/c/3ee859e384d453d6ac68bfd5971f630d9fa46ad3
- https://git.kernel.org/stable/c/4633a79ff8bc82770486a063a08b55e5162521d8
- https://git.kernel.org/stable/c/6cbf4c731d7812518cd857c2cfc3da9fd120f6ae
- https://git.kernel.org/stable/c/941d5180c430ce5b0f7a3622ef9b76077bfa3d82
- https://git.kernel.org/stable/c/b63e120189fd92aff00096d11e2fc5253f60248b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48747.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48747
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
