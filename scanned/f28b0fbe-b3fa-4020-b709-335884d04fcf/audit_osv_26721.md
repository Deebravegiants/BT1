# [H] scsi: target: iscsi: Fix buffer overflow in lio_target_nacl_info_show()

## Summary
Severity: High
Advisory: CVE-2023-53676
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53676
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.197, >=5.11.0 <5.15.133, >=5.16.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: iscsi: Fix buffer overflow in lio_target_nacl_info_show()

The function lio_target_nacl_info_show() uses sprintf() in a loop to print
details for every iSCSI connection in a session without checking for the
buffer length. With enough iSCSI connections it's possible to overflow the
buffer provided by configfs and corrupt the memory.

This patch replaces sprintf() with sysfs_emit_at() that checks for buffer
boundries.

## References
- https://git.kernel.org/stable/c/0cac6cbb9908309352a5d30c1876882771d3da50
- https://git.kernel.org/stable/c/114b44dddea1f8f99576de3c0e6e9059012002fc
- https://git.kernel.org/stable/c/2cbe6a88fbdd6e8aeab358eef61472e2de43d6f6
- https://git.kernel.org/stable/c/4738bf8b2d3635c2944b81b2a84d97b8c8b0978d
- https://git.kernel.org/stable/c/5353df78c22623b42a71d51226d228a8413097e2
- https://git.kernel.org/stable/c/801f287c93ff95582b0a2d2163f12870a2f076d4
- https://git.kernel.org/stable/c/bbe3ff47bf09db8956bc2eeb49d2d514d256ad2a
- https://git.kernel.org/stable/c/df349e84c2cb0dd05d98c8e1189c26ab4b116083
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53676.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53676
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
