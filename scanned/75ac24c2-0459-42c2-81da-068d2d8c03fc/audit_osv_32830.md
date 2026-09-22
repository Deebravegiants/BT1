# [C] sunrpc: handle SVC_GARBAGE during svc auth processing as auth error

## Summary
Severity: Critical
Advisory: CVE-2025-38089
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-30
Source: https://osv.dev/vulnerability/CVE-2025-38089
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

sunrpc: handle SVC_GARBAGE during svc auth processing as auth error

tianshuo han reported a remotely-triggerable crash if the client sends a
kernel RPC server a specially crafted packet. If decoding the RPC reply
fails in such a way that SVC_GARBAGE is returned without setting the
rq_accept_statp pointer, then that pointer can be dereferenced and a
value stored there.

If it's the first time the thread has processed an RPC, then that
pointer will be set to NULL and the kernel will crash. In other cases,
it could create a memory scribble.

The server sunrpc code treats a SVC_GARBAGE return from svc_authenticate
or pg_authenticate as if it should send a GARBAGE_ARGS reply. RFC 5531
says that if authentication fails that the RPC should be rejected
instead with a status of AUTH_ERR.

Handle a SVC_GARBAGE return as an AUTH_ERROR, with a reason of
AUTH_BADCRED instead of returning GARBAGE_ARGS in that case. This
sidesteps the whole problem of touching the rpc_accept_statp pointer in
this situation and avoids the crash.

## References
- http://www.openwall.com/lists/oss-security/2025/07/02/2
- https://git.kernel.org/stable/c/353e75b55e583635bf71cde6abcec274dba05edd
- https://git.kernel.org/stable/c/599c489eea793821232a2f69a00fa57d82b0ac98
- https://git.kernel.org/stable/c/94d10a4dba0bc482f2b01e39f06d5513d0f75742
- https://git.kernel.org/stable/c/c90459cd58bb421d275337093d8e901e0ba748dd
- https://www.openwall.com/lists/oss-security/2025/07/02/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38089.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38089
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/keymaker-arch/NFSundown
