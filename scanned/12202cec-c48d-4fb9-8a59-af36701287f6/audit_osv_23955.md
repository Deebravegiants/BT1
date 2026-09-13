# [H] scsi: lpfc: Resolve NULL ptr dereference after an ELS LOGO is aborted

## Summary
Severity: High
Advisory: CVE-2022-49730
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49730
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Resolve NULL ptr dereference after an ELS LOGO is aborted

A use-after-free crash can occur after an ELS LOGO is aborted.

Specifically, a nodelist structure is freed and then
ndlp->vport->cfg_log_verbose is dereferenced in lpfc_nlp_get() when the
discovery state machine is mistakenly called a second time with
NLP_EVT_DEVICE_RM argument.

Rework lpfc_cmpl_els_logo() to prevent the duplicate calls to release a
nodelist structure.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://git.kernel.org/stable/c/5e83869e29448958f8ae2c6911f350318f75e4fc
- https://git.kernel.org/stable/c/b1b3440f437b75fb2a9b0cfe58df461e40eca474
- https://git.kernel.org/stable/c/eea34ce23dc3a595695856dc73bb132a9c5a2902
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49730.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49730
