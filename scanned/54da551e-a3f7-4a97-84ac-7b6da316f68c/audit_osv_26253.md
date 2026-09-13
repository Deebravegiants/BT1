# [M] fs/ntfs3: Fix an NULL dereference bug

## Summary
Severity: Medium
Advisory: CVE-2023-52631
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2023-52631
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.149, >=5.16.0 <6.1.78, >=6.2.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Fix an NULL dereference bug

The issue here is when this is called from ntfs_load_attr_list().  The
"size" comes from le32_to_cpu(attr->res.data_size) so it can't overflow
on a 64bit systems but on 32bit systems the "+ 1023" can overflow and
the result is zero.  This means that the kmalloc will succeed by
returning the ZERO_SIZE_PTR and then the memcpy() will crash with an
Oops on the next line.

## References
- https://git.kernel.org/stable/c/686820fe141ea0220fc6fdfc7e5694f915cf64b2
- https://git.kernel.org/stable/c/ae4acad41b0f93f1c26cc0fc9135bb79d8282d0b
- https://git.kernel.org/stable/c/b2dd7b953c25ffd5912dda17e980e7168bebcf6c
- https://git.kernel.org/stable/c/ec1bedd797588fe38fc11cba26d77bb1d9b194c6
- https://git.kernel.org/stable/c/fb7bcd1722bc9bc55160378f5f99c01198fd14a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52631.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52631
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
