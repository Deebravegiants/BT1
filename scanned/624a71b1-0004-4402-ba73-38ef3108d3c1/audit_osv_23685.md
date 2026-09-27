# [M] scsi: lpfc: Address NULL pointer dereference after starget_to_rport()

## Summary
Severity: Medium
Advisory: CVE-2022-49332
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49332
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Address NULL pointer dereference after starget_to_rport()

Calls to starget_to_rport() may return NULL.  Add check for NULL rport
before dereference.

## References
- https://git.kernel.org/stable/c/68fcff1127e4995ddbd4b6861892a25c23db3f70
- https://git.kernel.org/stable/c/6f808bd78e8296b4ded813b7182988d57e1f6176
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49332.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49332
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
