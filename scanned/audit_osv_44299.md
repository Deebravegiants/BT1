# [H] pmdomain: mediatek: mfg: initialize prev_o in mtk_mfg_attach_dev()

## Summary
Severity: High
Advisory: CVE-2026-80751
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80751
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

pmdomain: mediatek: mfg: initialize prev_o in mtk_mfg_attach_dev()

mtk_mfg_attach_dev() reads prev_o on the first iteration of its loop,
in "if (prev_o && prev_o->freq == o->freq)", before prev_o is assigned
at the end of the loop body. On that first iteration, evaluating prev_o
reads an indeterminate value. If it is non-NULL, the condition
dereferences a stale or invalid pointer, potentially faulting or
incorrectly skipping the first OPP.

Initialize prev_o to NULL. This matches the intent as well: there is no
previous OPP to compare against on the first iteration.

Found with Clang's -Wconditional-uninitialized.

## References
- https://git.kernel.org/stable/c/090a95dbe13df9965279b588d97eda134831769c
- https://git.kernel.org/stable/c/de4eec0dfde8c0e27f8915bbb244d17ff68f2fb4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80751.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80751
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
