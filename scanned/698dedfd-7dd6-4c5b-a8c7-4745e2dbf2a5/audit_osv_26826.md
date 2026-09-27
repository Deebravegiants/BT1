# [H] mtd: rawnand: fsl_upm: Fix an off-by one test in fun_exec_op()

## Summary
Severity: High
Advisory: CVE-2023-54104
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54104
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.190, >=5.11.0 <5.15.126, >=5.16.0 <6.1.45, >=6.2.0 <6.4.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: rawnand: fsl_upm: Fix an off-by one test in fun_exec_op()

'op-cs' is copied in 'fun->mchip_number' which is used to access the
'mchip_offsets' and the 'rnb_gpio' arrays.
These arrays have NAND_MAX_CHIPS elements, so the index must be below this
limit.

Fix the sanity check in order to avoid the NAND_MAX_CHIPS value. This
would lead to out-of-bound accesses.

## References
- https://git.kernel.org/stable/c/1f09d67d390647f83f8f9d26382b0daa43756e6f
- https://git.kernel.org/stable/c/49e57caf967a969f6b955c88805f2d160910aa12
- https://git.kernel.org/stable/c/c6abce60338aa2080973cd95be0aedad528bb41f
- https://git.kernel.org/stable/c/eb7a5e4d14c8659cb97db6863316280e15f67209
- https://git.kernel.org/stable/c/f4b700c71802c81e6f9dce362ee7a0312c8377ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54104.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54104
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
