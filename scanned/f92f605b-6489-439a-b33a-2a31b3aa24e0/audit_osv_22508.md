# [M] CVE-2022-3106

## Summary
Severity: Medium
Advisory: CVE-2022-3106
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3106
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. ef100_update_stats in drivers/net/ethernet/sfc/ef100_nic.c lacks check of the return value of kmalloc().

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=407ecd1bd726f240123f704620d46e285ff30dd9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3106.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3106
- https://bugzilla.redhat.com/show_bug.cgi?id=2153066
