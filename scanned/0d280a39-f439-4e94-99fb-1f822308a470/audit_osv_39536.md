# [H] net: strparser: fix skb_head leak in strp_abort_strp()

## Summary
Severity: High
Advisory: CVE-2026-46102
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46102
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: strparser: fix skb_head leak in strp_abort_strp()

When the stream parser is aborted, for example after a message assembly timeout,
it can still hold a reference to a partially assembled message in
strp->skb_head.

That skb is not released in strp_abort_strp(), which leaks the partially
assembled message and can be triggered repeatedly to exhaust memory.

Fix this by freeing strp->skb_head and resetting the parser state in the
abort path. Leave strp_stop() unchanged so final cleanup still happens in
strp_done() after the work and timer have been synchronized.

## References
- https://git.kernel.org/stable/c/19ca9475f18f991735f98a22e735c43e95e6298d
- https://git.kernel.org/stable/c/5327dad2ffe9c1b49881dd6d51ff3c6893847568
- https://git.kernel.org/stable/c/56082f442023db9be1a5a29d4ee361de4017c0b7
- https://git.kernel.org/stable/c/a470ed71c906cc8cbad0d74c9942216698911f8b
- https://git.kernel.org/stable/c/c2e57695ec9ff9d42f23de70f3805199153d007b
- https://git.kernel.org/stable/c/d6668ce0e78d23eabecef9a6bc4f0f739cb28ad3
- https://git.kernel.org/stable/c/e9ae00490d474757c0f9c65073de83e6bb1e5a00
- https://git.kernel.org/stable/c/fe72340daaf1af588be88056faf98965f39e6032
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46102.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46102
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
