# [M] drm/msm: Avoid NULL dereference in msm_disp_state_print_regs()

## Summary
Severity: Medium
Advisory: CVE-2024-50156
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50156
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: Avoid NULL dereference in msm_disp_state_print_regs()

If the allocation in msm_disp_state_dump_regs() failed then
`block->state` can be NULL. The msm_disp_state_print_regs() function
_does_ have code to try to handle it with:

  if (*reg)
    dump_addr = *reg;

...but since "dump_addr" is initialized to NULL the above is actually
a noop. The code then goes on to dereference `dump_addr`.

Make the function print "Registers not stored" when it sees a NULL to
solve this. Since we're touching the code, fix
msm_disp_state_print_regs() not to pointlessly take a double-pointer
and properly mark the pointer as `const`.

Patchwork: https://patchwork.freedesktop.org/patch/619657/

## References
- https://git.kernel.org/stable/c/293f53263266bc4340d777268ab4328a97f041fa
- https://git.kernel.org/stable/c/42cf045086feae77b212f0f66e742b91a5b566b7
- https://git.kernel.org/stable/c/563aa81fd66a4e7e6e551a0e02bcc23957cafe2f
- https://git.kernel.org/stable/c/e8e9f2a12a6214080c8ea83220a596f6e1dedc6c
- https://git.kernel.org/stable/c/f7ad916273483748582d97cfa31054ccb19224f3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50156.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50156
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
