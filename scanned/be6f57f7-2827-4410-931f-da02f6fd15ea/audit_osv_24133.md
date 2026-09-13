# [H] jbd2: fix potential use-after-free in jbd2_fc_wait_bufs

## Summary
Severity: High
Advisory: CVE-2022-50328
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50328
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

jbd2: fix potential use-after-free in jbd2_fc_wait_bufs

In 'jbd2_fc_wait_bufs' use 'bh' after put buffer head reference count
which may lead to use-after-free.
So judge buffer if uptodate before put buffer head reference count.

## References
- https://git.kernel.org/stable/c/1d4d16daec2a6689b6d3fbfc7d2078643adc6619
- https://git.kernel.org/stable/c/243d1a5d505d0b0460c9af0ad56ed4a56ef0bebd
- https://git.kernel.org/stable/c/2e6d9f381c1ed844531a577783fc352de7a44c8a
- https://git.kernel.org/stable/c/d11d2ded293976a1a0d9d9471827a44dc9e3c63f
- https://git.kernel.org/stable/c/effd9b3c029ecdd853a11933dcf857f5a7ca8c3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50328.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50328
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
