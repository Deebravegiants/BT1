# [H] nfc: llcp: add missing return after LLCP_CLOSED checks

## Summary
Severity: High
Advisory: CVE-2026-31629
Aliases: A-499350302, ASB-A-499350302
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31629
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: llcp: add missing return after LLCP_CLOSED checks

In nfc_llcp_recv_hdlc() and nfc_llcp_recv_disc(), when the socket
state is LLCP_CLOSED, the code correctly calls release_sock() and
nfc_llcp_sock_put() but fails to return. Execution falls through to
the remainder of the function, which calls release_sock() and
nfc_llcp_sock_put() again. This results in a double release_sock()
and a refcount underflow via double nfc_llcp_sock_put(), leading to
a use-after-free.

Add the missing return statements after the LLCP_CLOSED branches
in both functions to prevent the fall-through.

## References
- https://git.kernel.org/stable/c/0eb1263a3b8c36418c9ba295c9ab3abed664edbf
- https://git.kernel.org/stable/c/2b5dd4632966c39da6ba74dbc8689b309065e82c
- https://git.kernel.org/stable/c/665315df9c3486cb213fc44d83cc8bcd47fe0d26
- https://git.kernel.org/stable/c/796e0cac058252d0ad34ebe288e6f7979b5fc9b2
- https://git.kernel.org/stable/c/8977fad2b3c6eefd414131168d597c5d1d5e1abf
- https://git.kernel.org/stable/c/9b49e2a4b8219a2fc5cebf94f4ec34e509aff8a6
- https://git.kernel.org/stable/c/aba4712e8f0381cd5d196534ce2ad082626a5ab6
- https://git.kernel.org/stable/c/b2a23529593d011fb433a3d711fc597ed6a6bd2f
- https://git.kernel.org/stable/c/ff3d9e8f7244293e303f7b6ef70774291c7c27e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31629.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31629
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
