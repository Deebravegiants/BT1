# [H] batman-adv: bla: avoid double decrement of bla.num_requests

## Summary
Severity: High
Advisory: CVE-2026-64095
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64095
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: bla: avoid double decrement of bla.num_requests

The bla.num_requests is increased when no request_sent was in progress. And
it is decremented in various places (announcement was received, backbone is
purged, periodic work). But the check if the request_sent is actually set
to a specific state and the atomic_dec/_inc are not safe because they are
not atomic (TOCTOU) and multiple such code portions can run concurrently.

At the same time, it is necessary to modify request_sent (state) and
bla.num_requests atomically. Otherwise batadv_bla_send_request() might set
request_sent to 1 and is interrupted.  batadv_handle_announce() can then
set request_sent back to 0 and decrement num_requests before
batadv_bla_send_request() incremented it.

The two operations must therefore be locked. And since state (request_sent)
and wait_periods are only accessed inside this lock, they can be converted
to simpler datatypes. And to avoid that the bla.num_requests is touched by
a parallel running context with a valid backbone_gw reference after
batadv_bla_purge_backbone_gw() ran, a third state "stopped" is required to
correctly signal that a backbone_gw is in the state of being cleaned up.

## References
- https://git.kernel.org/stable/c/1f013bc94154f2e78e97d0296175664224c796e0
- https://git.kernel.org/stable/c/45384612f29692fbf0c770200361a7acff90125c
- https://git.kernel.org/stable/c/461f1e3dfb888701895b766446c55db2b10db705
- https://git.kernel.org/stable/c/5328b95960774f2e189f22485616bc7b8eb2f7e3
- https://git.kernel.org/stable/c/65497ad155a3246df177b5ef662cd6e5a32cb470
- https://git.kernel.org/stable/c/83ab69bd12b80f6ea169c8bea6977701b53a043d
- https://git.kernel.org/stable/c/8ff9c59d1b7b48c2596878341a5310f32895d52b
- https://git.kernel.org/stable/c/a9393751ecf7e9096f93cb6eed02db4f79125765
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64095.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64095
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
