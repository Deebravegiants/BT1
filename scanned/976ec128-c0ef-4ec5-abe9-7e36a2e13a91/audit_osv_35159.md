# [C] scsi: qla2xxx: Clear cmds after chip reset

## Summary
Severity: Critical
Advisory: CVE-2025-68745
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68745
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Clear cmds after chip reset

Commit aefed3e5548f ("scsi: qla2xxx: target: Fix offline port handling
and host reset handling") caused two problems:

1. Commands sent to FW, after chip reset got stuck and never freed as FW
   is not going to respond to them anymore.

2. BUG_ON(cmd->sg_mapped) in qlt_free_cmd().  Commit 26f9ce53817a
   ("scsi: qla2xxx: Fix missed DMA unmap for aborted commands")
   attempted to fix this, but introduced another bug under different
   circumstances when two different CPUs were racing to call
   qlt_unmap_sg() at the same time: BUG_ON(!valid_dma_direction(dir)) in
   dma_unmap_sg_attrs().

So revert "scsi: qla2xxx: Fix missed DMA unmap for aborted commands" and
partially revert "scsi: qla2xxx: target: Fix offline port handling and
host reset handling" at __qla2x00_abort_all_cmds.

## References
- https://git.kernel.org/stable/c/5c1fb3fd05da3d55b8cbc42d7d660b313cbdc936
- https://git.kernel.org/stable/c/d46c69a087aa3d1513f7a78f871b80251ea0c1ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68745.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68745
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
