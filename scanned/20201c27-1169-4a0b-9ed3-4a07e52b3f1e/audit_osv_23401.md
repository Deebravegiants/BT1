# [H] scsi: mpt3sas: Fix use-after-free warning

## Summary
Severity: High
Advisory: CVE-2022-48695
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2022-48695
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.9.328, >=4.10.0 <4.14.293, >=4.15.0 <4.19.258, >=4.20.0 <5.4.213, >=5.5.0 <5.10.143, >=5.11.0 <5.15.68, >=5.16.0 <5.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpt3sas: Fix use-after-free warning

Fix the following use-after-free warning which is observed during
controller reset:

refcount_t: underflow; use-after-free.
WARNING: CPU: 23 PID: 5399 at lib/refcount.c:28 refcount_warn_saturate+0xa6/0xf0

## References
- https://git.kernel.org/stable/c/41acb064c4e013808bc7d5fc1b506fa449425b0b
- https://git.kernel.org/stable/c/5682c94644fde72f72bded6580c38189ffc856b5
- https://git.kernel.org/stable/c/6229fa494a5949be209bc73afbc5d0a749c2e3c7
- https://git.kernel.org/stable/c/82efb917eeb27454dc4c6fe26432fc8f6c75bc16
- https://git.kernel.org/stable/c/991df3dd5144f2e6b1c38b8d20ed3d4d21e20b34
- https://git.kernel.org/stable/c/b8fc9e91b931215110ba824d1a2983c5f60b6f82
- https://git.kernel.org/stable/c/d4959d09b76eb7a4146f5133962b88d3bddb63d6
- https://git.kernel.org/stable/c/ea10a652ad2ae2cf3eced6f632a5c98f26727057
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48695.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48695
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
