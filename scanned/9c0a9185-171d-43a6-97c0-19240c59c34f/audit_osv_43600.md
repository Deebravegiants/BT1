# [H] drm/amd/pm: fix pptable use-after-free

## Summary
Severity: High
Advisory: CVE-2026-74450
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74450
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/pm: fix pptable use-after-free

amdgpu_dpm_get_pp_table() returns a pointer to a driver-owned power table
after dropping adev->pm.mutex. The sysfs path then copies from that pointer.
A concurrent pp_table write can replace and free the allocation during the
copy, causing a use-after-free.

Change the DPM interface to copy into caller-provided storage while the mutex
is held. Keep the size-only query for attribute discovery without exposing
the driver-owned pointer.

(cherry picked from commit f6eed7acfd30099ef7baeb6ba45bb59daad80631)

## References
- https://git.kernel.org/stable/c/3fbb3ac75000e3187f500a91a4099b24206866a1
- https://git.kernel.org/stable/c/81b5af1fb0f14cace6c3b3130a05e5602a597820
- https://git.kernel.org/stable/c/8c685df5c3b261c42505110965b42f9a754eb9b7
- https://git.kernel.org/stable/c/9efc767335234cf7a892e46d45cd453b711421e7
- https://git.kernel.org/stable/c/b628f2c6feb3a115ea72d3120a2bd94afc5163df
- https://git.kernel.org/stable/c/bb493058c35c8676e48269ab6732688ea733d23c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74450
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
