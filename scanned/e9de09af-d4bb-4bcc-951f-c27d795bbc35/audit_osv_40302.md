# [C] sctp: purge outqueue on stale COOKIE-ECHO handling

## Summary
Severity: Critical
Advisory: CVE-2026-52924
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52924
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: purge outqueue on stale COOKIE-ECHO handling

sctp_stream_update() is only invoked when the association is moved into
COOKIE_WAIT during association setup/reconfiguration. In this path, the
outbound stream scheduler state (stream->out_curr) is expected to be
clean, since no user data should have been transmitted yet unless the
state machine has already partially progressed.

However, a corner case exists in sctp_sf_do_5_2_6_stale(): when a
Stale Cookie ERROR is received, the association is rolled back from
COOKIE_ECHOED to COOKIE_WAIT. In this scenario, user data may already
have been queued and even bundled with the COOKIE-ECHO chunk.

During the rollback, sctp_stream_update() frees the old stream table
and installs a new one, but it does not invalidate stream->out_curr.
As a result, out_curr may still point to a freed sctp_stream_out
entry from the previous stream state.

Later, SCTP scheduler dequeue paths (FCFS, RR, PRIO, etc.) rely on
stream->out_curr->ext, which can lead to use-after-free once the old
stream state has been released via sctp_stream_free().

This results in crashes such as (reported by Yuqi):

  BUG: KASAN: slab-use-after-free in sctp_sched_fcfs_dequeue+0x13a/0x140
  Read of size 8 at addr ff1100004d4d3208 by task mini_poc/9312
  CPU: 1 UID: 1001 PID: 9312 Comm: mini_poc Not tainted
     7.1.0-rc1-00305-gbd3a4795d574 #5 PREEMPT(full)
   sctp_sched_fcfs_dequeue+0x13a/0x140
   sctp_outq_flush+0x1603/0x33e0
   sctp_do_sm+0x31c9/0x5d30
   sctp_assoc_bh_rcv+0x392/0x6f0
   sctp_inq_push+0x1db/0x270
   sctp_rcv+0x138d/0x3c10

Fix this by fully purging the association outqueue when handling the
Stale Cookie case. This ensures all pending transmit and retransmit
state is dropped, and any scheduler cached pointers are invalidated,
making it safe to rebuild stream state during COOKIE_WAIT restart.

Updating only stream->out_curr would be insufficient, since queued
and retransmittable data would still reference the old stream state and
trigger later use-after-free in dequeue paths.

## References
- https://git.kernel.org/stable/c/1d4652f677906a64487c13f9ace54b0eb263b5d0
- https://git.kernel.org/stable/c/2afc9e684dc7fecf73db1edc937ebbc47b4b68dc
- https://git.kernel.org/stable/c/3c0741a441a7df7099d7ca6a64a6a0de09c677c8
- https://git.kernel.org/stable/c/83ade59e5da365f4bf8bce72c5a38774202b442f
- https://git.kernel.org/stable/c/84b7a319105db2f917ccdcf502bdc866082b1285
- https://git.kernel.org/stable/c/a6207349e703cfc04756a4d16dec9176135813a5
- https://git.kernel.org/stable/c/e374b22e9b07b72a25909621464ff74096151bfb
- https://git.kernel.org/stable/c/f46e1d1a758878f0d22c4fbbd1bf42bb7165d1e8
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52924.json
- https://access.redhat.com/errata/RHSA-2026:59723
- https://access.redhat.com/errata/RHSA-2026:59737
- https://access.redhat.com/errata/RHSA-2026:59821
- https://access.redhat.com/security/cve/CVE-2026-52924
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52924.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52924
- https://bugzilla.redhat.com/show_bug.cgi?id=2492095
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
