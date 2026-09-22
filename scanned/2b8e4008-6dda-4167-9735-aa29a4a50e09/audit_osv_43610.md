# [H] scsi: scsi_debug: Fix REPORT ZONES alloc_len underflow OOB write

## Summary
Severity: High
Advisory: CVE-2026-74470
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74470
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.217, >=5.16.0 <6.6.151, >=6.2.0 <6.12.103, >=6.7.0 <6.18.44, >=6.13.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: scsi_debug: Fix REPORT ZONES alloc_len underflow OOB write

resp_report_zones() sizes the reply buffer from the CDB allocation
length. The v3 fix rounds alloc_len up with ALIGN() before deriving the
descriptor count:

	rep_max_zones = (ALIGN((u64)alloc_len, RZONES_DESC_HD) -
			 RZONES_DESC_HD) >> ilog2(RZONES_DESC_HD);
	arr_len = (u64)RZONES_DESC_HD * (rep_max_zones + 1);

For alloc_len in 0xFFFFFFC1..0xFFFFFFFF, ALIGN() rounds up to
0x100000000, so arr_len is 4 GB. On 32-bit, kzalloc()'s size_t is 32-bit
and truncates 0x100000000 to 0; kzalloc(0) returns ZERO_SIZE_PTR, which
passes the !arr check, and desc = arr + 64 is then dereferenced in the
loop -> out-of-bounds write / panic.

Clamp rep_max_zones to devip->nr_zones. The loop already stops at
sdebug_capacity (after nr_zones zones), so a report can never hold more
than nr_zones descriptors; the clamp does not change the report, it only
bounds arr_len to (nr_zones + 1) * RZONES_DESC_HD, a real device
property that can never reach 0x100000000.

## References
- https://git.kernel.org/stable/c/2047ed09bf13453b7d6f9431b112ec07984dd69b
- https://git.kernel.org/stable/c/495058429ca55ab7fcc21977b63b92907ad68066
- https://git.kernel.org/stable/c/49e5b25a0b74dbac595f122e5608fdce2918cc4e
- https://git.kernel.org/stable/c/5d3e1d006bbb543259f9e31824caadbfff6a5465
- https://git.kernel.org/stable/c/7b615fc139e35c81077046df44725c532f7e2404
- https://git.kernel.org/stable/c/93dde0bf2f39a0f9f57fd610aa3201ce5b753433
- https://git.kernel.org/stable/c/d6e6da6bc3b53231fac77ffab428da8173ee729c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74470.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74470
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
