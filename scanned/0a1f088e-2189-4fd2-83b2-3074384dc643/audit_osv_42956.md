# [C] sunrpc: harden rq_procinfo lifecycle to prevent double-free

## Summary
Severity: Critical
Advisory: CVE-2026-72220
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72220
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

sunrpc: harden rq_procinfo lifecycle to prevent double-free

The svc_release_rqst() function executes the callback inside
rqstp->rq_procinfo->pc_release. However, if a worker thread begins
processing a new request and encounters an early error path (e.g.,
unsupported protocol, short frame, or bad auth) before a valid
rq_procinfo is installed, a stale release hook can be re-triggered
against reused state from the previous RPC, resulting in a double-free
or use-after-free vulnerability.

Harden the lifecycle of rq_procinfo by:
1. Ensuring svc_release_rqst() always clears rq_procinfo after the
   optional pc_release() call, regardless of whether the hook exists.
2. Explicitly clearing rq_procinfo at request entry in svc_process()
   before any early decode or drop paths.
3. Ensuring svc_process_bc() does the same at backchannel entry.

This guarantees that error flows will not encounter a non-NULL stale
rq_procinfo pointer when there is nothing to release.

## References
- https://git.kernel.org/stable/c/18d216788bef06332ff8901670ecf1ed8f6eb614
- https://git.kernel.org/stable/c/31ba490c02d476a5e4f90b8845932ac9db8aa71b
- https://git.kernel.org/stable/c/66014ab165cb01bfef5836939412a8ef98d5d5ff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72220.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72220
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
