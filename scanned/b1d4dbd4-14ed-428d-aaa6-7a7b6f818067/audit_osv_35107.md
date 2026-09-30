# [C] f2fs: fix to detect potential corrupted nid in free_nid_list

## Summary
Severity: Critical
Advisory: CVE-2025-68315
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68315
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to detect potential corrupted nid in free_nid_list

As reported, on-disk footer.ino and footer.nid is the same and
out-of-range, let's add sanity check on f2fs_alloc_nid() to detect
any potential corruption in free_nid_list.

## References
- https://git.kernel.org/stable/c/6b9525596a83cd5b7bbc2c7bd5f9ad9cf5ad60fa
- https://git.kernel.org/stable/c/88b2ddb0c4f1dc874d4598e78cc830c64315ed86
- https://git.kernel.org/stable/c/8fc6056dcf79937c46c97fa4996cda65956437a9
- https://git.kernel.org/stable/c/9337ed5e777e1c19854928cba7a8131dd00e611b
- https://git.kernel.org/stable/c/adbcb34f03abb89e681a5907c4c3ce4bf224991d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68315.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68315
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
