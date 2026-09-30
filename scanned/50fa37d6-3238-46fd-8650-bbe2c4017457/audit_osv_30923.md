# [M] net/9p/usbg: fix handling of the failed kzalloc() memory allocation

## Summary
Severity: Medium
Advisory: CVE-2024-56730
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56730
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/9p/usbg: fix handling of the failed kzalloc() memory allocation

On the linux-next, next-20241108 vanilla kernel, the coccinelle tool gave the
following error report:

./net/9p/trans_usbg.c:912:5-11: ERROR: allocation function on line 911 returns
NULL not ERR_PTR on failure

kzalloc() failure is fixed to handle the NULL return case on the memory exhaustion.

## References
- https://git.kernel.org/stable/c/2cdb416de8b5795fd25fadcb69e1198b6df6d8cc
- https://git.kernel.org/stable/c/ff1060813d9347e8c45c8b8cff93a4dfdb6726ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56730.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56730
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
