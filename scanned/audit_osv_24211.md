# [M] crypto: hisilicon/hpre - fix resource leak in remove process

## Summary
Severity: Medium
Advisory: CVE-2022-50420
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2022-50420
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: hisilicon/hpre - fix resource leak in remove process

In hpre_remove(), when the disable operation of qm sriov failed,
the following logic should continue to be executed to release the
remaining resources that have been allocated, instead of returning
directly, otherwise there will be resource leakage.

## References
- https://git.kernel.org/stable/c/2b3e3ecdb402ff1053ee25b598ff21b9ddf4384f
- https://git.kernel.org/stable/c/45e6319bd5f2154d8b8c9f1eaa4ac030ba0d330c
- https://git.kernel.org/stable/c/4e0de941d252d4e7c985981e78480c8d6f020b64
- https://git.kernel.org/stable/c/cb873c93a7ad27681920bf062ef052fca1e8d5b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50420.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50420
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
