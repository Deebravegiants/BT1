# [H] media: nxp: imx8-isi: Fix potential out-of-bounds issues

## Summary
Severity: High
Advisory: CVE-2026-68219
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68219
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: nxp: imx8-isi: Fix potential out-of-bounds issues

The maximum downscaling factor supported by ISI can be up to 16. Add
minimum value constraint before applying the setting to hardware.
Otherwise, the process will not respond even when Ctrl+C is executed.

## References
- https://git.kernel.org/stable/c/28ae75dba701d7aa69a36802c398582933d3e0e6
- https://git.kernel.org/stable/c/57a7ec5c9f38ce6c4d6209c4b75c8e57e1fea6cf
- https://git.kernel.org/stable/c/690cdda752f3dc6b7a8b2d4a243e0207b66a1f37
- https://git.kernel.org/stable/c/75cdfaa7c908ca06d564170da9c80fb579f149a5
- https://git.kernel.org/stable/c/ba7e1b06cbdad3b7c3314390cca22aff42f655d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68219.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68219
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
