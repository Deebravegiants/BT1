# [H] rxrpc: Fix oops due to non-existence of prealloc backlog struct

## Summary
Severity: High
Advisory: CVE-2025-38514
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38514
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.189, >=5.16.0 <6.1.146, >=6.2.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix oops due to non-existence of prealloc backlog struct

If an AF_RXRPC service socket is opened and bound, but calls are
preallocated, then rxrpc_alloc_incoming_call() will oops because the
rxrpc_backlog struct doesn't get allocated until the first preallocation is
made.

Fix this by returning NULL from rxrpc_alloc_incoming_call() if there is no
backlog struct.  This will cause the incoming call to be aborted.

## References
- https://git.kernel.org/stable/c/0eef29385d715d4c7fd707b18d4a9b76c76dd5e6
- https://git.kernel.org/stable/c/2c2e9ebeb036f9b1b09325ec5cfdfe0e78f357c3
- https://git.kernel.org/stable/c/880a88f318cf1d2a0f4c0a7ff7b07e2062b434a4
- https://git.kernel.org/stable/c/bf0ca6a1bc4fb904b598137c6718785a107e3adf
- https://git.kernel.org/stable/c/d1ff5f9d2c5405681457262e23c720b08977c11f
- https://git.kernel.org/stable/c/efc1b2b7c1a308b60df8f36bc2d7ce16d3999364
- https://git.kernel.org/stable/c/f5e72b7824d08c206ce106d30cb37c4642900ccc
- https://git.kernel.org/stable/c/f7afb3ff01c42c49e8a143cdce400b95844bb506
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38514.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38514
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
