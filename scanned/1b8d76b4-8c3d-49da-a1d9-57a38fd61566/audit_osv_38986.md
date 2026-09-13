# [H] media: qcom: camss: vfe: Fix out-of-bounds access in vfe_isr_reg_update()

## Summary
Severity: High
Advisory: CVE-2026-43256
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43256
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.167, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: qcom: camss: vfe: Fix out-of-bounds access in vfe_isr_reg_update()

vfe_isr() iterates using MSM_VFE_IMAGE_MASTERS_NUM(7) as the loop
bound and passes the index to vfe_isr_reg_update(). However,
vfe->line[] array is defined with VFE_LINE_NUM_MAX(4):

    struct vfe_line line[VFE_LINE_NUM_MAX];

When index is 4, 5, 6, the access to vfe->line[line_id] exceeds
the array bounds and resulting in out-of-bounds memory access.

Fix this by using separate loops for output lines and write masters.

## References
- https://git.kernel.org/stable/c/0c074e80921fd18984b75836730d76c768c84f65
- https://git.kernel.org/stable/c/1b103307df6d461a0731be25aca69ad0335b0933
- https://git.kernel.org/stable/c/d965919af524e68cb2ab1a685872050ad2ee933d
- https://git.kernel.org/stable/c/e6cbf765686fb6c1d8f2530b3daf6c66efc92f5d
- https://git.kernel.org/stable/c/e7a38ecda2498e7ce998793ac2a46ca47317635d
- https://git.kernel.org/stable/c/fade67c88870f497a13ed450ba01f7236c92dd9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43256.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43256
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
