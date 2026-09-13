# [H] staging: vt6655: fix potential memory leak

## Summary
Severity: High
Advisory: CVE-2022-50758
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50758
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: vt6655: fix potential memory leak

In function device_init_td0_ring, memory is allocated for member
td_info of priv->apTD0Rings[i], with i increasing from 0. In case of
allocation failure, the memory is freed in reversed order, with i
decreasing to 0. However, the case i=0 is left out and thus memory is
leaked.

Modify the memory freeing loop to include the case i=0.

## References
- https://git.kernel.org/stable/c/16a45e78a687eb6c69acc4e62b94b6508b0bfbda
- https://git.kernel.org/stable/c/1b3cebeca99e8e0aa4fa57faac8dbf41e967317a
- https://git.kernel.org/stable/c/c8ff91535880d41b49699b3829fb6151942de29e
- https://git.kernel.org/stable/c/cfdf139258614ef65b0f68b857ada5328fb7c0e5
- https://git.kernel.org/stable/c/e741e38aa98704fbb959650ecd270b71b2670680
- https://git.kernel.org/stable/c/fb5f569bcda8f87bd47d8030bfae343d757fa3ea
- https://git.kernel.org/stable/c/ff8551d411f12b5abc5ca929ab87643afa8a9588
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50758.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50758
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
