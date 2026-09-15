# [H] accel/ivpu: Reject firmware log with size smaller than header

## Summary
Severity: High
Advisory: CVE-2026-72089
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72089
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.148, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Reject firmware log with size smaller than header

fw_log_from_bo() validates the tracing buffer header_size and that the
log fits within the BO, but never checks that log->size is at least
log->header_size. fw_log_print_buffer() then computes:

  u32 data_size = log->size - log->header_size;

which underflows to a near-U32_MAX value when firmware reports a log whose
size is smaller than its header. That huge data_size defeats the
log_start/log_end bounds clamps added by commit dd1311bcf0e6 ("accel/ivpu:
Add bounds checks for firmware log indices"), so fw_log_print_lines() reads
far past the small real data region of the BO. A size of 0 also makes
fw_log_from_bo() advance the offset by 0, causing the callers to loop
forever on the same header.

Reject logs whose size is smaller than the header (which also rejects
size == 0).

## References
- https://git.kernel.org/stable/c/257321a1c036da417f5d9c47b95c7e58f62bf263
- https://git.kernel.org/stable/c/5592a207e158b738d9c1d27f208dbbea13ae7606
- https://git.kernel.org/stable/c/6920e62be4c969a68ce4ebc59da68c6cbc9512e5
- https://git.kernel.org/stable/c/dc9a1cda2e46d0254730a6f93cfe48532895f33c
- https://git.kernel.org/stable/c/ddb44baed257560f192b145ed36cf8c0a412de47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72089.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72089
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
