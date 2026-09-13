# [H] bpf: Check sk_state before sk_protocol in bpf_tcp_*_syncookie

## Summary
Severity: High
Advisory: CVE-2026-80738
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80738
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Check sk_state before sk_protocol in bpf_tcp_*_syncookie

bpf_tcp_gen_syncookie and bpf_tcp_check_syncookie accept a socket pointer
'sk' with argument type ARG_PTR_TO_BTF_ID_SOCK_COMMON. However, they access
sk->sk_protocol without validating whether 'sk' represents a full socket.

Fix this issue by checking sk->sk_state != TCP_LISTEN before inspecting
sk->sk_protocol in both bpf_tcp_gen_syncookie and bpf_tcp_check_syncookie.
Since mini-sockets are never in the TCP_LISTEN state, the condition
short-circuits and prevents dereferencing fullsock-specific fields.

## References
- https://git.kernel.org/stable/c/23f682083aa3fbc0c49667818efd6979a8bc5ac2
- https://git.kernel.org/stable/c/31a420a822ff92e2090bd5d65efe8e34e2d6d9b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80738.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80738
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
