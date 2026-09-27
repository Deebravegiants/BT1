# [M] CVE-2022-3110

## Summary
Severity: Medium
Advisory: CVE-2022-3110
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3110
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. _rtw_init_xmit_priv in drivers/staging/r8188eu/core/rtw_xmit.c lacks check of the return value of rtw_alloc_hwxmits() and will cause the null pointer dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=f94b47c6bde624d6c07f43054087607c52054a95
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3110.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3110
- https://bugzilla.redhat.com/show_bug.cgi?id=2153055
