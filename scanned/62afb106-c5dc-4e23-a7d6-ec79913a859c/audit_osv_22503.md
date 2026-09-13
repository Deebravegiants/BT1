# [M] CVE-2022-3105

## Summary
Severity: Medium
Advisory: CVE-2022-3105
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3105
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. uapi_finalize in drivers/infiniband/core/uverbs_uapi.c lacks check of kmalloc_array().

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=7694a7de22c53a312ea98960fcafc6ec62046531
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3105.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3105
- https://bugzilla.redhat.com/show_bug.cgi?id=2153067
