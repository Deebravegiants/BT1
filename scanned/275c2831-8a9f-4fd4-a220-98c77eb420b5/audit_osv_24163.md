# [H] powercap: intel_rapl: fix UBSAN shift-out-of-bounds issue

## Summary
Severity: High
Advisory: CVE-2022-50366
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50366
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

powercap: intel_rapl: fix UBSAN shift-out-of-bounds issue

When value < time_unit, the parameter of ilog2() will be zero and
the return value is -1. u64(-1) is too large for shift exponent
and then will trigger shift-out-of-bounds:

shift exponent 18446744073709551615 is too large for 32-bit type 'int'
Call Trace:
 rapl_compute_time_window_core
 rapl_write_data_raw
 set_time_window
 store_constraint_time_window_us

## References
- https://git.kernel.org/stable/c/139bbbd01114433b80fe59f5e1330615aadf9752
- https://git.kernel.org/stable/c/1d94af37565e4d3c26b0d63428e093a37d5b4c32
- https://git.kernel.org/stable/c/2d93540014387d1c73b9ccc4d7895320df66d01b
- https://git.kernel.org/stable/c/3eb0ba70376f6ee40fa843fc9cee49269370b0b3
- https://git.kernel.org/stable/c/42f79dbb9514f726ff21df25f09cb0693b0b2445
- https://git.kernel.org/stable/c/49a6ffdaed60f0eb52c198fafebc05994e16e305
- https://git.kernel.org/stable/c/4ebba43384722adbd325baec3a12c572d94488eb
- https://git.kernel.org/stable/c/6216b685b8f48ab7b721a6fd5acbf526b41c13e8
- https://git.kernel.org/stable/c/708b9abe1b4a2f050a483db4b7edfc446b13df1f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50366.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50366
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
