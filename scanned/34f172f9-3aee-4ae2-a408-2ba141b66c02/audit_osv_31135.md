# [H] rxrpc: Fix handling of received connection abort

## Summary
Severity: High
Advisory: CVE-2024-58053
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58053
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix handling of received connection abort

Fix the handling of a connection abort that we've received.  Though the
abort is at the connection level, it needs propagating to the calls on that
connection.  Whilst the propagation bit is performed, the calls aren't then
woken up to go and process their termination, and as no further input is
forthcoming, they just hang.

Also add some tracing for the logging of connection aborts.

## References
- https://git.kernel.org/stable/c/0e56ebde245e4799ce74d38419426f2a80d39950
- https://git.kernel.org/stable/c/5842ce7b120c65624052a8da04460d35b26caac0
- https://git.kernel.org/stable/c/96d1d927c4d03ee9dcee7640bca70b74e63504fc
- https://git.kernel.org/stable/c/9c6702260557c0183d8417c79a37777a3d3e58e8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58053.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58053
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
