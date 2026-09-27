# [M] nfsd: call op_release, even when op_func returns an error

## Summary
Severity: Medium
Advisory: CVE-2023-53241
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53241
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.220, >=5.11.0 <5.15.154, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: call op_release, even when op_func returns an error

For ops with "trivial" replies, nfsd4_encode_operation will shortcut
most of the encoding work and skip to just marshalling up the status.
One of the things it skips is calling op_release. This could cause a
memory leak in the layoutget codepath if there is an error at an
inopportune time.

Have the compound processing engine always call op_release, even when
op_func sets an error in op->status. With this change, we also need
nfsd4_block_get_device_info_scsi to set the gd_device pointer to NULL
on error to avoid a double free.

## References
- https://git.kernel.org/stable/c/15a8b55dbb1ba154d82627547c5761cac884d810
- https://git.kernel.org/stable/c/3d0dcada384af22dec764c8374a2997870ec86ae
- https://git.kernel.org/stable/c/65a33135e91e6dd661ecdf1194b9d90c49ae3570
- https://git.kernel.org/stable/c/b11d8162c24af4a351d21e2c804d25ca493305e3
- https://git.kernel.org/stable/c/b623a8e5d38a69a3ef8644acb1030dd7c7bc28b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53241.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53241
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
