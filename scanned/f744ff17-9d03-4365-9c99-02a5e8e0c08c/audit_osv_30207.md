# [M] scsi: lpfc: Ensure DA_ID handling completion before deleting an NPIV instance

## Summary
Severity: Medium
Advisory: CVE-2024-50183
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50183
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Ensure DA_ID handling completion before deleting an NPIV instance

Deleting an NPIV instance requires all fabric ndlps to be released before
an NPIV's resources can be torn down.  Failure to release fabric ndlps
beforehand opens kref imbalance race conditions.  Fix by forcing the DA_ID
to complete synchronously with usage of wait_queue.

## References
- https://git.kernel.org/stable/c/0857b1c573c0b095aa778bb26d8b3378172471b6
- https://git.kernel.org/stable/c/0a3c84f71680684c1d41abb92db05f95c09111e8
- https://git.kernel.org/stable/c/0ef6e016eb53fad6dc44c3253945efb43a3486b9
- https://git.kernel.org/stable/c/bbc525409bfe8e5bff12f5d18d550ab3e52cdbef
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50183.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50183
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
