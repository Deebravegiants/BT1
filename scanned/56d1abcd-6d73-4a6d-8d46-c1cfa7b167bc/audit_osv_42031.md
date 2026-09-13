# [H] smb: client: fix double-free in SMB2_open() replay

## Summary
Severity: High
Advisory: CVE-2026-64382
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64382
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.96, >=6.8.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix double-free in SMB2_open() replay

A response-bearing attempt can return a replayable error and free its
response buffer. If SMB2_open_init() fails before the next send, cleanup
retains the previous buffer type and frees that response again.

Reset response bookkeeping before each attempt to prevent the stale free.

## References
- https://git.kernel.org/stable/c/02bc2896bdc3e29362d6e40d404006944a159c25
- https://git.kernel.org/stable/c/14498ff5ce0f272ce0ef988721413e06b7038972
- https://git.kernel.org/stable/c/3196b5192f246df4272072f61a2f4a3e9967f55d
- https://git.kernel.org/stable/c/b55e182f2324bc6a604c21a47aa6c448f719a532
- https://git.kernel.org/stable/c/ff2d30927bc3bf3c629f0768d2068096e64ef5ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64382.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64382
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
