# [C] net/tcp-md5: Fix MAC comparison to be constant-time

## Summary
Severity: Critical
Advisory: CVE-2026-43383
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43383
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <5.10.253, >=5.11.0 <5.15.210, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tcp-md5: Fix MAC comparison to be constant-time

To prevent timing attacks, MACs need to be compared in constant
time.  Use the appropriate helper function for this.

## References
- https://git.kernel.org/stable/c/02669e2a4d207068edce7e8b5fafd85822018ce6
- https://git.kernel.org/stable/c/345a9530756528d7ca407663d659c3c40e75c3dd
- https://git.kernel.org/stable/c/46d0d6f50dab706637f4c18a470aac20a21900d3
- https://git.kernel.org/stable/c/5d305a95130a8d08b9545e47f1e18d29d59866cb
- https://git.kernel.org/stable/c/821c8751fdeecdeecabeb11704dd33439c9e4bbc
- https://git.kernel.org/stable/c/ae3831b44f477de048287493e184fc3ff913b624
- https://git.kernel.org/stable/c/b502e97e29d791ff7a8051f29a414535739be218
- https://git.kernel.org/stable/c/ff44ec94d4fc8348600a69de0a8fa1102c23bce8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43383.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
