# [H] netfilter: nf_tables: adapt set backend to use GC transaction API

## Summary
Severity: High
Advisory: CVE-2023-52923
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-20
Source: https://osv.dev/vulnerability/CVE-2023-52923
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.19.316, >=4.20.0 <5.4.262, >=5.5.0 <5.10.198, >=5.11.0 <5.15.134, >=5.16.0 <6.1.56, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: adapt set backend to use GC transaction API

Use the GC transaction API to replace the old and buggy gc API and the
busy mark approach.

No set elements are removed from async garbage collection anymore,
instead the _DEAD bit is set on so the set element is not visible from
lookup path anymore. Async GC enqueues transaction work that might be
aborted and retried later.

rbtree and pipapo set backends does not set on the _DEAD bit from the
sync GC path since this runs in control plane path where mutex is held.
In this case, set elements are deactivated, removed and then released
via RCU callback, sync GC never fails.

## References
- https://git.kernel.org/stable/c/146c76866795553dbc19998f36718d7986ad302b
- https://git.kernel.org/stable/c/479a2cf5259347d6a1f658b0f791d27a34908e91
- https://git.kernel.org/stable/c/c357648929c8dff891502349769aafb8f0452bc2
- https://git.kernel.org/stable/c/cb4d00b563675ba8ff6ef94b077f58d816f68ba3
- https://git.kernel.org/stable/c/df650d6a4bf47248261b61ef6b174d7c54034d15
- https://git.kernel.org/stable/c/e4d71d6a9c7db93f7bf20c3a0f0659d63d7de681
- https://git.kernel.org/stable/c/f6c383b8c31a93752a52697f8430a71dcbc46adf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52923.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52923
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
