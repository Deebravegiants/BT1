# [H] scsi: pm8001: Fix use-after-free for aborted TMF sas_task

## Summary
Severity: High
Advisory: CVE-2022-48791
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48791
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.102, >=5.11.0 <5.15.25, >=5.14.0 <5.16.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: pm8001: Fix use-after-free for aborted TMF sas_task

Currently a use-after-free may occur if a TMF sas_task is aborted before we
handle the IO completion in mpi_ssp_completion(). The abort occurs due to
timeout.

When the timeout occurs, the SAS_TASK_STATE_ABORTED flag is set and the
sas_task is freed in pm8001_exec_internal_tmf_task().

However, if the I/O completion occurs later, the I/O completion still
thinks that the sas_task is available. Fix this by clearing the ccb->task
if the TMF times out - the I/O completion handler does nothing if this
pointer is cleared.

## References
- https://git.kernel.org/stable/c/3c334cdfd94945b8edb94022a0371a8665b17366
- https://git.kernel.org/stable/c/510b21442c3a2e3ecc071ba3e666b320e7acdd61
- https://git.kernel.org/stable/c/61f162aa4381845acbdc7f2be4dfb694d027c018
- https://git.kernel.org/stable/c/d872e7b5fe38f325f5206b6872746fa02c2b4819
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48791.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48791
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
