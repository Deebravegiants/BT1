# [H] SUNRPC: Fix the svc_deferred_event trace class

## Summary
Severity: High
Advisory: CVE-2022-49065
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49065
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.112, >=5.11.0 <5.15.35, >=5.16.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: Fix the svc_deferred_event trace class

Fix a NULL deref crash that occurs when an svc_rqst is deferred
while the sunrpc tracing subsystem is enabled. svc_revisit() sets
dr->xprt to NULL, so it can't be relied upon in the tracepoint to
provide the remote's address.

Unfortunately we can't revert the "svc_deferred_class" hunk in
commit ece200ddd54b ("sunrpc: Save remote presentation address in
svc_xprt for trace events") because there is now a specific check
of event format specifiers for unsafe dereferences. The warning
that check emits is:

  event svc_defer_recv has unsafe dereference of argument 1

A "%pISpc" format specifier with a "struct sockaddr *" is indeed
flagged by this check.

Instead, take the brute-force approach used by the svcrdma_qp_error
tracepoint. Convert the dr::addr field into a presentation address
in the TP_fast_assign() arm of the trace event, and store that as
a string. This fix can be backported to -stable kernels.

In the meantime, commit c6ced22997ad ("tracing: Update print fmt
check to handle new __get_sockaddr() macro") is now in v5.18, so
this wonky fix can be replaced with __sockaddr() and friends
properly during the v5.19 merge window.

## References
- https://git.kernel.org/stable/c/4d5004451ab2218eab94a30e1841462c9316ba19
- https://git.kernel.org/stable/c/726ae7300fcc25fefa46d188cc07eb16dc908f9e
- https://git.kernel.org/stable/c/85ee17ca21cf92989e8c923e3ea4514c291e9d38
- https://git.kernel.org/stable/c/c2456f470eea3bd06574d988bf6089e7c3f4c5cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49065.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49065
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
