# [C] netfilter: ipset: Don't use test_bit() in lockless RCU readers in hash types

## Summary
Severity: Critical
Advisory: CVE-2026-72436
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72436
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: Don't use test_bit() in lockless RCU readers in hash types

Sashiko pointed out that there are a few lockless RCU readers
using test_bit() which is a relaxed atomic operation and
provides no memory barrier guarantees. Use test_bit_acquire()
instead where the operation may run parallel with add/del/gc,
i.e. is not one from the next cases

- protected by region lock
- in a set destroy phase
- in a new/temporary set creation phase

## References
- https://git.kernel.org/stable/c/3219d74e4536658c937fd878a327257b86ce80dd
- https://git.kernel.org/stable/c/6329d3a9afe715fddda0460cfa46b496d61c2fe0
- https://git.kernel.org/stable/c/7445fe965b7d8756070a40e80f8b73348ccda1d7
- https://git.kernel.org/stable/c/c107233d2ff4fd7cef5d02f9124b99194957a710
- https://git.kernel.org/stable/c/c4d257734e91bfcdc71d41843392dd6400b5bb1b
- https://git.kernel.org/stable/c/e4b4984e28c16406ecb318444dea4a8bf47def3e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72436.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72436
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
