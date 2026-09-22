# [H] ksmbd: fix Out-of-Bounds Write in ksmbd_vfs_stream_write

## Summary
Severity: High
Advisory: CVE-2024-56626
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56626
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.176, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix Out-of-Bounds Write in ksmbd_vfs_stream_write

An offset from client could be a negative value, It could allows
to write data outside the bounds of the allocated buffer.
Note that this issue is coming when setting
'vfs objects = streams_xattr parameter' in ksmbd.conf.

## References
- https://git.kernel.org/stable/c/164d3597d26d9acff5d5b8bc3208bdcca942dd6a
- https://git.kernel.org/stable/c/1aea5c9470be2c7129704fb1b9562b1e3e0576f8
- https://git.kernel.org/stable/c/313dab082289e460391c82d855430ec8a28ddf81
- https://git.kernel.org/stable/c/8cd7490fc0f268883e86e840cda5311257af69ca
- https://git.kernel.org/stable/c/c5797f195c67132d061d29c57a7c6d30530686f0
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56626.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56626
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
