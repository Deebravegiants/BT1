# [C] inet: frags: publish queues before arming timer

## Summary
Severity: Critical
Advisory: CVE-2026-74662
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74662
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

inet: frags: publish queues before arming timer

inet_frag_create() arms the fragment queue timer before inserting the
queue into the fqdir rhashtable. If the namespace fragment timeout is
zero or negative, the timer can run before the queue is published.

The timer callback then marks the queue complete, tries to remove a node
that is not in the hash table yet, and drops the anticipated hash
reference. Creation can subsequently publish the completed queue without
restoring that reference, leaving a stale hash node after the caller drops
the remaining reference.

Publish the queue first and arm the timer while holding the queue lock.
This makes timer expiry wait until the queue is visible in the hash table,
so inet_frag_kill() can remove the node and balance the hash reference.

## References
- https://git.kernel.org/stable/c/08a04d7bfb9c103432561aff8a62b6872e694a6a
- https://git.kernel.org/stable/c/39c6c4b267b65f00e0b0335a2ae00cbe9e3174f0
- https://git.kernel.org/stable/c/4ed0681dc2c1e0538b79d2fc56190ffcb369dacd
- https://git.kernel.org/stable/c/653d7ddf6cba867777a3d14c4f83ace008c5ad13
- https://git.kernel.org/stable/c/928128865e43b197e30688dc1bc991592c97edcf
- https://git.kernel.org/stable/c/9f904dd3e455750e5d4ec9b2f134835811b85a2f
- https://git.kernel.org/stable/c/d3ffb89b2944672cf7bdd8e9ee577d2043b4a956
- https://git.kernel.org/stable/c/f4e4dab62181b7fe7c011bed6fbef9fc3d48c769
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74662.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74662
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
