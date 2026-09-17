# [H] udf: refactor inode_bmap() to handle error

## Summary
Severity: High
Advisory: CVE-2024-50211
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50211
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: refactor inode_bmap() to handle error

Refactor inode_bmap() to handle error since udf_next_aext() can return
error now. On situations like ftruncate, udf_extend_file() can now
detect errors and bail out early without resorting to checking for
particular offsets and assuming internal behavior of these functions.

## References
- https://git.kernel.org/stable/c/493447dd8336607fce426f7879e581095f6c606e
- https://git.kernel.org/stable/c/b22d9a5698abf04341f8fbc30141e0673863c3a6
- https://git.kernel.org/stable/c/c226964ec786f3797ed389a16392ce4357697d24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50211.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50211
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
