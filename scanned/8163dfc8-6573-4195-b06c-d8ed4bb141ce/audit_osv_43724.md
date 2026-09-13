# [H] net/dibs: Correct freeing of dmb_clientid_arr

## Summary
Severity: High
Advisory: CVE-2026-74629
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74629
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/dibs: Correct freeing of dmb_clientid_arr

A dibs device interrupt handler can be active after dibs_dev_del() and
may still access dmb_clientid_arr. (UAF)

In case of a failure in dibs_dev_add() being called by dibs_lo_dev_probe()
dmb_clientid_arr is freed twice (double free).

Free dmb_clientid_arr in dibs_dev_release() after last reference is gone.
Note that allocating in dibs_dev_add() instead of dibs_dev_alloc() is ok
for now, because no dmbs can be registered before dibs_dev_add().

## References
- https://git.kernel.org/stable/c/7a1df20a8d2cc89e3a442b6e0b43b1cacde8d403
- https://git.kernel.org/stable/c/9e6869be49064915edb6c8776b27c376cfdb0df5
- https://git.kernel.org/stable/c/ece6426b61241e9bfb41aa131f235168f55229b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74629.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74629
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
