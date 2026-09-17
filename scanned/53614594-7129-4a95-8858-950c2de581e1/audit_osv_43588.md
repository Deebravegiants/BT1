# [H] rxrpc: Fix potential infinite loop in rxrpc_recvmsg()

## Summary
Severity: High
Advisory: CVE-2026-74431
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74431
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix potential infinite loop in rxrpc_recvmsg()

Fix the wait in rxrpc_recvmsg() also take check the oob queue.

## References
- https://git.kernel.org/stable/c/0fc5b37faec26241d3cbee732e29ac35ad3184f8
- https://git.kernel.org/stable/c/67a0332f442ef07713cd2d9c13d59db0f1c23648
- https://git.kernel.org/stable/c/da371b003a4a44f44741275d5e8dc74181cbb017
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74431.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74431
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
