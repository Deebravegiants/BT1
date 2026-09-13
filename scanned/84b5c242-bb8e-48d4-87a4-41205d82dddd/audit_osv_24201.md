# [M] crypto: hisilicon/qm - increase the memory of local variables

## Summary
Severity: Medium
Advisory: CVE-2022-50407
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50407
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: hisilicon/qm - increase the memory of local variables

Increase the buffer to prevent stack overflow by fuzz test. The maximum
length of the qos configuration buffer is 256 bytes. Currently, the value
of the 'val buffer' is only 32 bytes. The sscanf does not check the dest
memory length. So the 'val buffer' may stack overflow.

## References
- https://git.kernel.org/stable/c/34c4f8ad45b4ea814c7ecc3f23a2d292959d5a52
- https://git.kernel.org/stable/c/3efe90af4c0c46c58dba1b306de142827153d9c0
- https://git.kernel.org/stable/c/fc521abb6ee4b8f06fdfc52646140dab6a2ed334
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50407.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50407
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
