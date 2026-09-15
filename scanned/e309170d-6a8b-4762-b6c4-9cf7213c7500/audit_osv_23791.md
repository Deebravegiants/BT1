# [H] drm/msm/disp/dpu1: set vbif hw config to NULL to avoid use after memory free during pm runtime resume

## Summary
Severity: High
Advisory: CVE-2022-49489
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49489
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/disp/dpu1: set vbif hw config to NULL to avoid use after memory free during pm runtime resume

BUG: Unable to handle kernel paging request at virtual address 006b6b6b6b6b6be3

Call trace:
  dpu_vbif_init_memtypes+0x40/0xb8
  dpu_runtime_resume+0xcc/0x1c0
  pm_generic_runtime_resume+0x30/0x44
  __genpd_runtime_resume+0x68/0x7c
  genpd_runtime_resume+0x134/0x258
  __rpm_callback+0x98/0x138
  rpm_callback+0x30/0x88
  rpm_resume+0x36c/0x49c
  __pm_runtime_resume+0x80/0xb0
  dpu_core_irq_uninstall+0x30/0xb0
  dpu_irq_uninstall+0x18/0x24
  msm_drm_uninit+0xd8/0x16c

Patchwork: https://patchwork.freedesktop.org/patch/483255/
[DB: fixed Fixes tag]

## References
- https://git.kernel.org/stable/c/134760263f6441741db0b2970e7face6b34b6d1c
- https://git.kernel.org/stable/c/5b0adf5cbf3b74721e4e4c4e0cadc91b8df8bcc2
- https://git.kernel.org/stable/c/97ac682b6f7d36be5d934f86c9911066540a68f1
- https://git.kernel.org/stable/c/aa4cb188988dc6f1b3f4917d4dbc452150a5d871
- https://git.kernel.org/stable/c/ef10d0c68e8608848cd58fca2589685718426607
- https://git.kernel.org/stable/c/ef4bdaac7cb5416f236613ed9337ff0ea8ee329b
- https://git.kernel.org/stable/c/fa5186b279ecf44b14fb435540d2065be91cb1ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49489.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49489
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
