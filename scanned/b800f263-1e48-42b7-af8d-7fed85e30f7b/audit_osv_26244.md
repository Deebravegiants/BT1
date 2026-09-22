# [H] PM / devfreq: Fix buffer overflow in trans_stat_show

## Summary
Severity: High
Advisory: CVE-2023-52614
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2023-52614
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.216, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

PM / devfreq: Fix buffer overflow in trans_stat_show

Fix buffer overflow in trans_stat_show().

Convert simple snprintf to the more secure scnprintf with size of
PAGE_SIZE.

Add condition checking if we are exceeding PAGE_SIZE and exit early from
loop. Also add at the end a warning that we exceeded PAGE_SIZE and that
stats is disabled.

Return -EFBIG in the case where we don't have enough space to write the
full transition table.

Also document in the ABI that this function can return -EFBIG error.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/087de000e4f8c878c81d9dd3725f00a1d292980c
- https://git.kernel.org/stable/c/08e23d05fa6dc4fc13da0ccf09defdd4bbc92ff4
- https://git.kernel.org/stable/c/796d3fad8c35ee9df9027899fb90ceaeb41b958f
- https://git.kernel.org/stable/c/8a7729cda2dd276d7a3994638038fb89035b6f2c
- https://git.kernel.org/stable/c/a979f56aa4b93579cf0e4265ae04d7e9300fd3e8
- https://git.kernel.org/stable/c/eaef4650fa2050147ca25fd7ee43bc0082e03c87
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52614.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52614
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
