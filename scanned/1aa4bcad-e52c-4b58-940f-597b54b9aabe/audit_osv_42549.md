# [H] firmware: arm_ffa: Fix out-of-bound writes in ffa_setup_and_transmit()

## Summary
Severity: High
Advisory: CVE-2026-68401
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68401
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_ffa: Fix out-of-bound writes in ffa_setup_and_transmit()

Sashiko (locally) reports multiple out-of-bound issues in
ffa_setup_and_transmit:
1) Writing ep_mem_access->reserved can write out of bounds for FFA
   versions < 1.2 as ffa_emad_size_get() returns 16 bytes in that case
   while reserved has an offset of 24.
   Instead of zeroing fields, memset the struct to zero first based on
   the FFA version.

2) Make sure there is enough size to write constituents.

While at it, convert the only sizeof() in the driver that uses a
type instead of variable.

## References
- https://git.kernel.org/stable/c/27abdaf0c5c89b06694e4c3d8318e8d6a60c1d1b
- https://git.kernel.org/stable/c/3383ffb7ef937317361713ffcc21921a7848511a
- https://git.kernel.org/stable/c/cf5708c9d78c98214c62b1e5d049cd527a543b8e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68401.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68401
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
