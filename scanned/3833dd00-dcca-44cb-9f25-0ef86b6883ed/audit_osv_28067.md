# [C] SUNRPC: fix some memleaks in gssx_dec_option_array

## Summary
Severity: Critical
Advisory: CVE-2024-27388
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27388
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: fix some memleaks in gssx_dec_option_array

The creds and oa->data need to be freed in the error-handling paths after
their allocation. So this patch add these deallocations in the
corresponding paths.

## References
- https://git.kernel.org/stable/c/3cfcfc102a5e57b021b786a755a38935e357797d
- https://git.kernel.org/stable/c/5e6013ae2c8d420faea553d363935f65badd32c3
- https://git.kernel.org/stable/c/934212a623cbab851848b6de377eb476718c3e4c
- https://git.kernel.org/stable/c/9806c2393cd2ab0a8e7bb9ffae02ce20e3112ec4
- https://git.kernel.org/stable/c/996997d1fb2126feda550d6adcedcbd94911fc69
- https://git.kernel.org/stable/c/b97c37978ca825557d331c9012e0c1ddc0e42364
- https://git.kernel.org/stable/c/bb336cd8d5ecb69c430ebe3e7bcff68471d93fa8
- https://git.kernel.org/stable/c/bfa9d86d39a0fe4685f90c3529aa9bd62a9d97a8
- https://git.kernel.org/stable/c/dd292e884c649f9b1c18af0ec75ca90b390cd044
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27388.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27388
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
