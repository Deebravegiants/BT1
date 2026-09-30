# [H] net: slip: serialize receive against buffer reallocation

## Summary
Severity: High
Advisory: CVE-2026-68143
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68143
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: slip: serialize receive against buffer reallocation

sl_realloc_bufs() replaces rbuff and updates buffsize while holding
sl->lock. slip_receive_buf() reads those fields and writes through rbuff
without holding the lock.

An MTU change can therefore race with receive processing. An MTU shrink
can expose the new smaller rbuff with the old larger bound, causing an
out-of-bounds write. A receive callback which already loaded the old
rbuff can instead continue writing after that buffer has been freed.

Serialize receive processing with sl_realloc_bufs() by holding sl->lock
while consuming each receive batch.

## References
- https://git.kernel.org/stable/c/0e37bbd6d617eb52bace49390e99eaedc1af73ce
- https://git.kernel.org/stable/c/189a550eb7e1dc10018718ddfc46d003ffe58653
- https://git.kernel.org/stable/c/1be09d175b627fad7f6bec7ad27b8a4a99863912
- https://git.kernel.org/stable/c/44401f7dd9940ced7098930ef64f5a332f279fc2
- https://git.kernel.org/stable/c/5d07b178bef511d69558cfc89fe1129258dc39f8
- https://git.kernel.org/stable/c/8180daf2b66155f84ec4f9e3f95488c8a3421716
- https://git.kernel.org/stable/c/eb3836eab47487823f362e6985e170a1e15f20fd
- https://git.kernel.org/stable/c/ee7f9bb9320add61f7b367d7e6cd55e3a3a4d65d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68143.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68143
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
