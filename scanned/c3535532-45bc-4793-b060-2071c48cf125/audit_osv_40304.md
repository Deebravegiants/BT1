# [H] sctp: stream: fully roll back denied add-stream state

## Summary
Severity: High
Advisory: CVE-2026-52929
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52929
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: stream: fully roll back denied add-stream state

When ADD_OUT_STREAMS is denied, SCTP only shrinks the queued chunks and
then lowers outcnt. That leaves removed stream metadata behind, so a
later re-add can reuse a stale ext and hit a null-pointer dereference in
the scheduler get path.

Fix the rollback by tearing down the removed stream state the same way
other stream resizes do. Unschedule the current scheduler state, drop
the removed stream ext state with sctp_stream_outq_migrate(), and then
reschedule the remaining streams.

This keeps scheduler-private RR/FC/PRIO lists consistent while fully
rolling back denied outgoing stream additions.

## References
- https://git.kernel.org/stable/c/0cd2dc6dce8ca47212cd306ccd52eb315ef3cf85
- https://git.kernel.org/stable/c/1c6773b8c081509dcd5cd2954f2b02c50c00f151
- https://git.kernel.org/stable/c/39dc2b0eb5371a669ebc9ec6072b9184eac95418
- https://git.kernel.org/stable/c/7dd9a42b044aad2dbe037db1c1e2943582485b44
- https://git.kernel.org/stable/c/9662eb0401518f0b4681f10e7fbf688f504f24cf
- https://git.kernel.org/stable/c/a5f8a90ac9f77c678a9781c0a464b635e0d63e49
- https://git.kernel.org/stable/c/a6724b7b812ac8793514a1d5938db5d9d29ae725
- https://git.kernel.org/stable/c/d5ea0b3e261fcb2cfff142675516165244cab1da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52929.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52929
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
