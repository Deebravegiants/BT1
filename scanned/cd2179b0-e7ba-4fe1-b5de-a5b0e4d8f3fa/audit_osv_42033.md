# [C] smb: client: fix change notify replay double-free

## Summary
Severity: Critical
Advisory: CVE-2026-64384
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64384
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.96, >=6.8.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix change notify replay double-free

A response-bearing attempt can return a replayable error and free its
response buffer. If SMB2_notify_init() fails before the next send, cleanup
retains the previous buffer type and frees that response again.

Reset response bookkeeping before each attempt to prevent the stale free.

## References
- https://git.kernel.org/stable/c/145f820dcbb2cced374f2532f8a61a44dce4a615
- https://git.kernel.org/stable/c/52af1975f0dfae990c5a0e85872cc41be0e88a68
- https://git.kernel.org/stable/c/5821f9dbb8b5b24391850a13418e633edd0fb003
- https://git.kernel.org/stable/c/901891513951bc8322ece754863909ea45af95c6
- https://git.kernel.org/stable/c/d684f4134998085702009b94c35c2003fc9e72d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64384.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64384
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
