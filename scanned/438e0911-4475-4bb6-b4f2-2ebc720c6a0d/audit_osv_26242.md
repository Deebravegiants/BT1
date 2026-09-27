# [H] crypto: scomp - fix req->dst buffer overflow

## Summary
Severity: High
Advisory: CVE-2023-52612
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2023-52612
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.306, >=4.20.0 <5.4.268, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: scomp - fix req->dst buffer overflow

The req->dst buffer size should be checked before copying from the
scomp_scratch->dst to avoid req->dst buffer overflow problem.

## References
- https://git.kernel.org/stable/c/1142d65c5b881590962ad763f94505b6dd67d2fe
- https://git.kernel.org/stable/c/4518dc468cdd796757190515a9be7408adc8911e
- https://git.kernel.org/stable/c/4df0c942d04a67df174195ad8082f6e30e7f71a5
- https://git.kernel.org/stable/c/71c6670f9f032ec67d8f4e3f8db4646bf5a62883
- https://git.kernel.org/stable/c/744e1885922a9943458954cfea917b31064b4131
- https://git.kernel.org/stable/c/7d9e5bed036a7f9e2062a137e97e3c1e77fb8759
- https://git.kernel.org/stable/c/a5f2f91b3fd7387e5102060809316a0f8f0bc625
- https://git.kernel.org/stable/c/e0e3f4a18784182cfe34e20c00eca11e78d53e76
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52612.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52612
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
