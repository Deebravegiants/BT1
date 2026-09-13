# [C] sctp: fix use-after-free of cached ASCONF chunk

## Summary
Severity: Critical
Advisory: CVE-2026-74587
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74587
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: fix use-after-free of cached ASCONF chunk

addip_last_asconf caches the outstanding outbound ASCONF chunk. The normal
ASCONF-ACK completion path releases the chunk and clears the pointer.

However, sctp_asconf_queue_teardown() releases the cached chunk without
clearing addip_last_asconf. During peer restart handling,
sctp_sf_do_dupcook_a() queues SCTP_CMD_PURGE_ASCONF_QUEUE, which invokes
sctp_asconf_queue_teardown() while the association remains alive and leaves
the pointer dangling.

A delayed authenticated ASCONF-ACK can then reach sctp_sf_do_asconf_ack(),
which accesses the stale chunk and passes it to sctp_process_asconf_ack(),
causing a use-after-free and a second release.

Clearing the pointer exposes a race with T4 expiry. Peer restart handling
queues the timer stop before the purge, but SCTP_CMD_TIMER_STOP uses
timer_delete(), which does not wait for a callback already running on
another CPU. Such a callback can reach sctp_sf_t4_timer_expire() after
the purge and dereference NULL.

Clear addip_last_asconf after releasing the cached chunk, and make
sctp_sf_t4_timer_expire() consume a stale T4 expiry if no outstanding
ASCONF remains.

## References
- https://git.kernel.org/stable/c/07daf4f9750104960a1d60831b2353c0d41f35fb
- https://git.kernel.org/stable/c/10459b03e2d9ee12435e96f587de4d4cacdbf435
- https://git.kernel.org/stable/c/179676f0166230c80053a392303485b37c93dd33
- https://git.kernel.org/stable/c/618b5c6d049896fcfabb91afc072954c92cb2693
- https://git.kernel.org/stable/c/8c283e7b56adce00193837f3311b06662466fb21
- https://git.kernel.org/stable/c/d949992bc3f00027a2c755e860a11950c75f6073
- https://git.kernel.org/stable/c/dc67d528c2fa939cec7fe3bf7f3089c8d281ca3d
- https://git.kernel.org/stable/c/e1bb114e09372fd6e03387ced9ef566da336ed6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74587.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74587
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
