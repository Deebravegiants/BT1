# [H] ALSA: asihpi: Fix potential OOB array access at reading cache

## Summary
Severity: High
Advisory: CVE-2026-64133
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64133
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: asihpi: Fix potential OOB array access at reading cache

find_control() to retrieve a cached info accesses the array with the
given index blindly, which may lead to an OOB array access.
Add a sanity check for avoiding it.

## References
- https://git.kernel.org/stable/c/34d0d492a2812b9289af14bca3573a89275965b2
- https://git.kernel.org/stable/c/61c5017c64e2ac9e10b70b14b17a079dbc0a805f
- https://git.kernel.org/stable/c/7b6f8c8eb93f02a74b1de8e521c0952af10d1f43
- https://git.kernel.org/stable/c/7b7d6572145c1dab2dd9bfb550b188e5f0ff3c3f
- https://git.kernel.org/stable/c/7d107239935793995bdc6cf29bb99e180bde4c28
- https://git.kernel.org/stable/c/8778386e4387b28f2bf8425d7ffc667c6294457f
- https://git.kernel.org/stable/c/e060e21fe9cca1e5eafd8a1c597026577771e8d9
- https://git.kernel.org/stable/c/ffa29cea7bf9a4ef2ea8084967f142e0301ac670
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64133.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
