# [H] drm/panthor: validate firmware interface structure sizes

## Summary
Severity: High
Advisory: CVE-2026-74451
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74451
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: validate firmware interface structure sizes

iface_fw_to_cpu_addr() only checks that the firmware-provided MCU virtual
address points inside the shared section. The returned pointer is later
used as a full firmware interface structure, so accepting an address near
the end of the shared section can still lead to out-of-bounds accesses.

Pass the expected object size to iface_fw_to_cpu_addr() and reject ranges
that do not fit entirely in the shared section.

## References
- https://git.kernel.org/stable/c/21c77486f5a60bb9c0433c21de62a5f25d5091f1
- https://git.kernel.org/stable/c/b921b8613790a3f9e78ab64017fa7149ef0b750c
- https://git.kernel.org/stable/c/c835f2b0b7167584832b516c9b0a26e9180d1d0b
- https://git.kernel.org/stable/c/ca41d9f3a21586bf29df53eec05152ecf2b2f94f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74451.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74451
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
