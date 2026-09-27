# [H] media: venus: Add a check for packet size after reading from shared memory

## Summary
Severity: High
Advisory: CVE-2025-39710
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39710
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: Add a check for packet size after reading from shared memory

Add a check to ensure that the packet size does not exceed the number of
available words after reading the packet header from shared memory. This
ensures that the size provided by the firmware is safe to process and
prevent potential out-of-bounds memory access.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/0520c89f6280d2b60ab537d5743601185ee7d8ab
- https://git.kernel.org/stable/c/2d8cea8310a245730816a1fd0c9fa4a5a3bdc68c
- https://git.kernel.org/stable/c/49befc830daa743e051a65468c05c2ff9e8580e6
- https://git.kernel.org/stable/c/7638bae4539dcebc3f68fda74ac35d73618ec440
- https://git.kernel.org/stable/c/ba567c2e52fbcf0e20502746bdaa79e911c2e8cf
- https://git.kernel.org/stable/c/ef09b96665f16f3f0bac4e111160e6f24f1f8791
- https://git.kernel.org/stable/c/f0cbd9386f974d310a0d20a02e4a1323e95ea654
- https://git.kernel.org/stable/c/f5b7a943055a4a106d40a03bacd940e28cc1955f
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39710.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39710
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
