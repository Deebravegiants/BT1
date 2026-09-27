# [M] CVE-2022-3107

## Summary
Severity: Medium
Advisory: CVE-2022-3107
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3107
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. netvsc_get_ethtool_stats in drivers/net/hyperv/netvsc_drv.c lacks check of the return value of kvmalloc_array() and will cause the null pointer dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=886e44c9298a6b428ae046e2fa092ca52e822e6a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3107.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3107
- https://bugzilla.redhat.com/show_bug.cgi?id=2153060
