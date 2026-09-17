# [H] fs/jfs: Add validity check for db_maxag and db_agpref

## Summary
Severity: High
Advisory: CVE-2023-52804
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52804
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.331, >=4.15.0 <4.19.300, >=4.20.0 <5.4.262, >=5.5.0 <5.10.202, >=5.11.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/jfs: Add validity check for db_maxag and db_agpref

Both db_maxag and db_agpref are used as the index of the
db_agfree array, but there is currently no validity check for
db_maxag and db_agpref, which can lead to errors.

The following is related bug reported by Syzbot:

UBSAN: array-index-out-of-bounds in fs/jfs/jfs_dmap.c:639:20
index 7936 is out of range for type 'atomic_t[128]'

Add checking that the values of db_maxag and db_agpref are valid
indexes for the db_agfree array.

## References
- https://git.kernel.org/stable/c/1f74d336990f37703a8eee77153463d65b67f70e
- https://git.kernel.org/stable/c/2323de34a3ae61a9f9b544c18583f71cea86721f
- https://git.kernel.org/stable/c/32bd8f1cbcf8b663e29dd1f908ba3a129541a11b
- https://git.kernel.org/stable/c/5013f8269887642cca784adc8db9b5f0b771533f
- https://git.kernel.org/stable/c/64933ab7b04881c6c18b21ff206c12278341c72e
- https://git.kernel.org/stable/c/a0649e2dd4a3595b5595a29d0064d047c2fae2fb
- https://git.kernel.org/stable/c/c6c8863fb3f57700ab583d875adda04caaf2278a
- https://git.kernel.org/stable/c/ce15b0f1a431168f07b1cc6c9f71206a2db5c809
- https://git.kernel.org/stable/c/dca403bb035a565bb98ecc1dda5d30f676feda40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52804.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52804
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
