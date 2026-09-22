# [H] rxrpc: Fix a race between socket set up and I/O thread creation

## Summary
Severity: High
Advisory: CVE-2024-49864
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49864
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix a race between socket set up and I/O thread creation

In rxrpc_open_socket(), it sets up the socket and then sets up the I/O
thread that will handle it.  This is a problem, however, as there's a gap
between the two phases in which a packet may come into rxrpc_encap_rcv()
from the UDP packet but we oops when trying to wake the not-yet created I/O
thread.

As a quick fix, just make rxrpc_encap_rcv() discard the packet if there's
no I/O thread yet.

A better, but more intrusive fix would perhaps be to rearrange things such
that the socket creation is done by the I/O thread.

## References
- https://git.kernel.org/stable/c/56e415202b8a17de6496f4023e545fcb66f118ec
- https://git.kernel.org/stable/c/bc212465326e8587325f520a052346f0b57360e6
- https://git.kernel.org/stable/c/c64f5fc95e9612fdf75587c8e21e494e614c18e2
- https://git.kernel.org/stable/c/cdf4bbbdb956d7426f687f38757ebca2a2759a0f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49864.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49864
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
