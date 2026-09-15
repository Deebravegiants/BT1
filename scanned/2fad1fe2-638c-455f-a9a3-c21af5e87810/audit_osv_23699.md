# [C] SUNRPC: Trap RDMA segment overflows

## Summary
Severity: Critical
Advisory: CVE-2022-49356
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49356
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: Trap RDMA segment overflows

Prevent svc_rdma_build_writes() from walking off the end of a Write
chunk's segment array. Caught with KASAN.

The test that this fix replaces is invalid, and might have been left
over from an earlier prototype of the PCL work.

## References
- https://git.kernel.org/stable/c/659f7568e09593945c221bf20217a82ebdfe1328
- https://git.kernel.org/stable/c/812c13521d4a72469c78ce06d8cdc8dc5b5557b5
- https://git.kernel.org/stable/c/ea26bf5eca1459b5a7824997d7823409ce38214e
- https://git.kernel.org/stable/c/f012e95b377c73c0283f009823c633104dedb337
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49356.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49356
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
