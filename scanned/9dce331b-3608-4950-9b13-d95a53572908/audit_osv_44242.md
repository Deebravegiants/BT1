# [H] cxl: Fix CXL_HEADERLOG_SIZE to match RAS Capability size

## Summary
Severity: High
Advisory: CVE-2026-80662
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80662
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl: Fix CXL_HEADERLOG_SIZE to match RAS Capability size

The CXL r4.0 8.2.4.17.7 RAS Capability Structure has total length 0x58
bytes (CXL_RAS_CAPABILITY_LENGTH); the Header Log occupies the trailing
64 bytes at offset 0x18.  CXL_HEADERLOG_SIZE was defined as SZ_512,
eight times the actual on-device size.

header_log_copy() reads CXL_HEADERLOG_SIZE_U32 (128) dwords from the
RAS capability iomap, overrunning the 88-byte mapping by 448 bytes.
The cxl_aer_uncorrectable_error trace event memcpy()s CXL_HEADERLOG_SIZE
(512) bytes from its source.  For the CPER caller the source is
struct cxl_ras_capability_regs::header_log[16] (64 bytes) embedded in a
stack-local cxl_cper_prot_err_work_data, so the memcpy reads 448 bytes
of kernel stack into the trace event ring buffer where userspace can
read it via tracefs.

Set CXL_HEADERLOG_SIZE to 64 and derive CXL_HEADERLOG_SIZE_U32 from it,
bringing all iomap readers into agreement on 16 dwords.  Userspace tools
such as rasdaemon have grown a dependency on the buggy 512-byte (128 u32)
header_log layout in the cxl_aer_uncorrectable_error trace event.  Add
CXL_HEADERLOG_TRACE_SIZE_U32 = 128 and use it for the trace event
__array and its memcpy to preserve that ABI.  Both callers now pass a
zero-filled u32[CXL_HEADERLOG_TRACE_SIZE_U32] staging buffer with only
the first CXL_HEADERLOG_SIZE_U32 (16) entries populated from hardware;
the remaining 112 u32s are zero-padded, keeping the 512-byte trace ring
buffer layout intact.

[ dj: Replaced 64 with SZ_64 per RichardC ]

## References
- https://git.kernel.org/stable/c/6fc1919a6f2ed541484dd1f6cd93374044f8fd3d
- https://git.kernel.org/stable/c/c268f949e219f9e179558e836f457f6c5fbec416
- https://git.kernel.org/stable/c/fc5eb0962a5e50d64e711817cc24d67df2d90528
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80662.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80662
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
