# [H] rxrpc: Only put the call ref if one was acquired

## Summary
Severity: High
Advisory: CVE-2026-31638
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31638
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Only put the call ref if one was acquired

rxrpc_input_packet_on_conn() can process a to-client packet after the
current client call on the channel has already been torn down.  In that
case chan->call is NULL, rxrpc_try_get_call() returns NULL and there is
no reference to drop.

The client-side implicit-end error path does not account for that and
unconditionally calls rxrpc_put_call().  This turns a protocol error
path into a kernel crash instead of rejecting the packet.

Only drop the call reference if one was actually acquired.  Keep the
existing protocol error handling unchanged.

## References
- https://git.kernel.org/stable/c/0c156aff8a2d4fa0d61db7837641975cf0e5452d
- https://git.kernel.org/stable/c/6331f1b24a3e85465f6454e003a3e6c22005a5c5
- https://git.kernel.org/stable/c/8299ca146489664e3c0c90a3b8900d8335b1ede4
- https://git.kernel.org/stable/c/9fb09861e2b8d1abfe2efaf260c9f1d30080ea38
- https://git.kernel.org/stable/c/b8f66447448d6c305a51413a67ec8ed26aa7d1dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31638.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31638
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
