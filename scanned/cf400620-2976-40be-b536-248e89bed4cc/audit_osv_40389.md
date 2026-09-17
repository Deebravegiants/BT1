# [H] net: bcmgenet: fix leaking free_bds

## Summary
Severity: High
Advisory: CVE-2026-53087
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53087
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bcmgenet: fix leaking free_bds

While reclaiming the tx queue we fast forward the write pointer to
drop any data in flight. These dropped frames are not added back
to the pool of free bds. We also need to tell the netdev that we
are dropping said data.

## References
- https://git.kernel.org/stable/c/150d06aae1839a6564ab200ef0e7291c3528bbb0
- https://git.kernel.org/stable/c/25ff3a3e47ea635ec08dc93e84dd2bfe15abfebb
- https://git.kernel.org/stable/c/3c3abbcfa05bad17965498ff7cc94c2418fa94b3
- https://git.kernel.org/stable/c/3f3168300efb839028328d720ab3962f91d6a0d0
- https://git.kernel.org/stable/c/52b9f80993698138b90e5ca3a72550a2501f2a96
- https://git.kernel.org/stable/c/ac4a29c331ecb5b10240c44247a8e010c95bc15b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53087.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
