# [M] libfuse: NULL Pointer Dereference and Memory Leak in io_uring Queue Initialization

## Summary
Severity: Medium
Advisory: CVE-2026-33179
Aliases: GHSA-x669-v3mq-r358
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33179
Type: osv

## Details
libfuse is the reference implementation of the Linux FUSE. From version 3.18.0 to before version 3.18.2, a NULL pointer dereference and memory leak in fuse_uring_init_queue allows a local user to crash the FUSE daemon or cause resource exhaustion. When numa_alloc_local fails during io_uring queue entry setup, the code proceeds with NULL pointers. When fuse_uring_register_queue fails, NUMA allocations are leaked and the function incorrectly returns success. Only the io_uring transport is affected; the traditional /dev/fuse path is not affected. PoC confirmed with AddressSanitizer/LeakSanitizer. This issue has been patched in version 3.18.2.

## References
- https://github.com/libfuse/libfuse/releases/tag/fuse-3.18.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33179.json
- https://github.com/libfuse/libfuse/security/advisories/GHSA-x669-v3mq-r358
- https://nvd.nist.gov/vuln/detail/CVE-2026-33179
- https://github.com/libfuse/libfuse/commit/7beb86c09b6ec5aab14dc25256ed8a5ad18554d7
