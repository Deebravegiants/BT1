# [H] xen/pvcalls: bound backend response req_id before indexing rsp[]

## Summary
Severity: High
Advisory: CVE-2026-72380
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72380
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xen/pvcalls: bound backend response req_id before indexing rsp[]

pvcalls_front_event_handler() takes req_id directly from the
backend-supplied ring response and uses it to index the fixed-size
bedata->rsp[] array for a memcpy() and a store, with no range check. A
malicious or buggy backend can set req_id past PVCALLS_NR_RSP_PER_RING
and drive an out-of-bounds write past the bedata allocation.

req_id was also declared int while the wire field rsp->req_id is u32, so
a range check on the signed value alone is insufficient: a backend
req_id of 0xffffffff becomes -1, passes a >= PVCALLS_NR_RSP_PER_RING
test and indexes bedata->rsp[-1]. Declare req_id as u32 so a single
bound covers both ends.

A backend that sends an out-of-range req_id has violated the wire
protocol, so rather than silently dropping the response, log once and
stop trusting the backend: set bedata->disabled. The event handler then
ignores further responses, and the request paths that wait for a
response return -EIO instead of blocking forever. This mirrors the
fatal-error handling xen-netback uses (xenvif_fatal_tx_err()).

The pvcalls frontend currently trusts its backend, so this is not a
classic-Xen security issue, but it matters for hardening PV frontends
against malicious backends (confidential and disaggregated deployments).

## References
- https://git.kernel.org/stable/c/d1297a9e2fd6ce08678b370d41bc980ca798f809
- https://git.kernel.org/stable/c/d33846c8dcc06b83b7acdeac1e8bfbb5c0c26cb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72380.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72380
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
