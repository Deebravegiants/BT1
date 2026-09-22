# [H] platform/x86: alienware-wmi-wmax: Fix `dmi_system_id` array

## Summary
Severity: High
Advisory: CVE-2025-38661
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38661
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: alienware-wmi-wmax: Fix `dmi_system_id` array

Add missing empty member to `awcc_dmi_table`.

## References
- https://git.kernel.org/stable/c/660bcd9f1f94e623e1316b869b2172b36eb516d7
- https://git.kernel.org/stable/c/8346c6af27f1c1410eb314f4be5875fdf1579a10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38661.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38661
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
