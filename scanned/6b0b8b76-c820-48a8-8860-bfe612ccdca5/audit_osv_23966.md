# [M] perf/x86/amd: fix potential integer overflow on shift of a int

## Summary
Severity: Medium
Advisory: CVE-2022-49748
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49748
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.231, >=5.5.0 <5.10.166, >=5.6.0 <5.15.91, >=5.11.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/x86/amd: fix potential integer overflow on shift of a int

The left shift of int 32 bit integer constant 1 is evaluated using 32 bit
arithmetic and then passed as a 64 bit function argument. In the case where
i is 32 or more this can lead to an overflow.  Avoid this by shifting
using the BIT_ULL macro instead.

## References
- https://git.kernel.org/stable/c/08245672cdc6505550d1a5020603b0a8d4a6dcc7
- https://git.kernel.org/stable/c/14cc13e433e1067557435b1adbf05608d7d47a93
- https://git.kernel.org/stable/c/a4d01fb87ece45d4164fd725890211ccf9a307a9
- https://git.kernel.org/stable/c/f84c9b72fb200633774704d8020f769c88a4b249
- https://git.kernel.org/stable/c/fbf7b0e4cef3b5470b610f14fb9faa5ee7f63954
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49748.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
