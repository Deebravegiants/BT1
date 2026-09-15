# [H] selinux: Add boundary check in put_entry()

## Summary
Severity: High
Advisory: CVE-2022-50200
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50200
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <4.14.291, >=4.15.0 <4.19.256, >=4.20.0 <5.4.211, >=5.5.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

selinux: Add boundary check in put_entry()

Just like next_entry(), boundary check is necessary to prevent memory
out-of-bound access.

## References
- https://git.kernel.org/stable/c/15ec76fb29be31df2bccb30fc09875274cba2776
- https://git.kernel.org/stable/c/2dabe6a872a5744865372eb30ea51e8ccd21305a
- https://git.kernel.org/stable/c/477722f31ad73aa779154d1d7e00825538389f76
- https://git.kernel.org/stable/c/7363a69d8ca8f0086f8e1196c8ddaf0e168614b1
- https://git.kernel.org/stable/c/90bdf50ae70c5571a277b5601e4f5df210831e0a
- https://git.kernel.org/stable/c/9605f50157cae00eb299e1189a6d708c84935ad8
- https://git.kernel.org/stable/c/adbfdaacde18faf6cd4e490764045375266b3fbd
- https://git.kernel.org/stable/c/dedd558d9765b72c66e5a53948e9f5abc3ece1f6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50200.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50200
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
