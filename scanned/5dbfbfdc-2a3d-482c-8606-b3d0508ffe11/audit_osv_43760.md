# [H] tcp: fix TFO max_qlen accounting across reuseport migration

## Summary
Severity: High
Advisory: CVE-2026-74696
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74696
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: fix TFO max_qlen accounting across reuseport migration

A listener's TCP_FASTOPEN max_qlen stops being accurate and lets through
far more pending Fast Open requests than it was configured for.

This only shows up with SO_REUSEPORT listener migration, where closing a
listener hands its still-pending TFO children over to a surviving one.

fastopenq.qlen is charged in tcp_fastopen_create_child() when the child
is created and uncharged in reqsk_fastopen_remove() when the handshake
completes.  The uncharge follows rsk_listener of the request the child
points at, and inet_reqsk_clone() has repointed the child at a new
request owned by the new listener, so the ++ and the -- land on two
different sockets.  The new listener's qlen drifts negative and its
limit no longer binds.

Charge the new listener during migration, like reqsk_queue_migrated()
already does for queue->young and queue->qlen.

## References
- https://git.kernel.org/stable/c/585fc5247d14939a561056aa2addd9b7c2b1f670
- https://git.kernel.org/stable/c/6e10ee56524a26b250229ad348637825646ddb88
- https://git.kernel.org/stable/c/a0ab2ba83e35159d81cec830a92e885ecf8139be
- https://git.kernel.org/stable/c/a66e869cf0c90c1e47ae75f72b6482acbfc808ff
- https://git.kernel.org/stable/c/b6247e0f96bd825ffb2005257f6177b5e642dee6
- https://git.kernel.org/stable/c/d974618b2097453778389d385e3741629c40e0a3
- https://git.kernel.org/stable/c/e98f0d80b9cccb5f828425d2004f9686e7d1ae24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74696.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
