# [H] netfilter: ipset: make sure gc is properly stopped

## Summary
Severity: High
Advisory: CVE-2026-72434
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72434
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: make sure gc is properly stopped

Sashiko noticed that when destroying a set,
cancel_delayed_work_sync() was called while gc
calls queue_delayed_work() unconditionally which
can lead not to properly shutting down the gc.

## References
- https://git.kernel.org/stable/c/12088da6add5b003657c8506c5b0fcef835083b8
- https://git.kernel.org/stable/c/4a597a87e2e2f608edb6be2c510dc826b4fdfb53
- https://git.kernel.org/stable/c/c78bd5195a5998094a5866df702fbeafda60dafb
- https://git.kernel.org/stable/c/c940d1b96248c3081b664ede5418078bdc7c8c07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72434.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72434
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
