# [C] rxrpc: Fix double unlock in rxrpc_recvmsg()

## Summary
Severity: Critical
Advisory: CVE-2026-74428
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74428
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix double unlock in rxrpc_recvmsg()

Fix a double unlock in rxrpc_recvmsg() when dealing with OOB messages.

## References
- https://git.kernel.org/stable/c/1297ae6aeebc3863cb437e42a1bc4cd6173e43d9
- https://git.kernel.org/stable/c/8cd8cf3052fff9a4b86b25734f610e4af03786d3
- https://git.kernel.org/stable/c/a2f299b4d5510147fa8629a6aba2869bbcc88aea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74428.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74428
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
