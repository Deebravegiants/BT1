# [H] RDMA/rtrs-srv: Avoid null pointer deref during path establishment

## Summary
Severity: High
Advisory: CVE-2024-50062
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50062
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rtrs-srv: Avoid null pointer deref during path establishment

For RTRS path establishment, RTRS client initiates and completes con_num
of connections. After establishing all its connections, the information
is exchanged between the client and server through the info_req message.
During this exchange, it is essential that all connections have been
established, and the state of the RTRS srv path is CONNECTED.

So add these sanity checks, to make sure we detect and abort process in
error scenarios to avoid null pointer deref.

## References
- https://git.kernel.org/stable/c/394b2f4d5e014820455af3eb5859eb328eaafcfd
- https://git.kernel.org/stable/c/b5d4076664465487a9a3d226756995b12fb73d71
- https://git.kernel.org/stable/c/b720792d7e8515bc695752e0ed5884e2ea34d12a
- https://git.kernel.org/stable/c/ccb8e44ae3e2391235f80ffc6be59bec6b889ead
- https://git.kernel.org/stable/c/d0e62bf7b575fbfe591f6f570e7595dd60a2f5eb
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50062.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50062
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
