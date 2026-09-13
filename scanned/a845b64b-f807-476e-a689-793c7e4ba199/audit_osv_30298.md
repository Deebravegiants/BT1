# [H] rxrpc: Fix missing locking causing hanging calls

## Summary
Severity: High
Advisory: CVE-2024-50294
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50294
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix missing locking causing hanging calls

If a call gets aborted (e.g. because kafs saw a signal) between it being
queued for connection and the I/O thread picking up the call, the abort
will be prioritised over the connection and it will be removed from
local->new_client_calls by rxrpc_disconnect_client_call() without a lock
being held.  This may cause other calls on the list to disappear if a race
occurs.

Fix this by taking the client_call_lock when removing a call from whatever
list its ->wait_link happens to be on.

## References
- https://git.kernel.org/stable/c/996a7208dadbf2cdda8d51444d5ee1fdd1ccbc92
- https://git.kernel.org/stable/c/b1fdb0bb3b6513f5bd26f92369fd6ac1a2422d8b
- https://git.kernel.org/stable/c/fc9de52de38f656399d2ce40f7349a6b5f86e787
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50294.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50294
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
