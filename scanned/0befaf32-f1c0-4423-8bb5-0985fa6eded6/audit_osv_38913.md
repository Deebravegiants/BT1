# [H] scsi: target: file: Use kzalloc_flex for aio_cmd

## Summary
Severity: High
Advisory: CVE-2026-43055
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43055
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: file: Use kzalloc_flex for aio_cmd

The target_core_file doesn't initialize the aio_cmd->iocb for the
ki_write_stream. When a write command fd_execute_rw_aio() is executed,
we may get a bogus ki_write_stream value, causing unintended write
failure status when checking iocb->ki_write_stream > max_write_streams
in the block device.

Let's just use kzalloc_flex when allocating the aio_cmd and let
ki_write_stream=0 to fix this issue.

## References
- https://git.kernel.org/stable/c/01f784fc9d0ab2a6dac45ee443620e517cb2a19b
- https://git.kernel.org/stable/c/4eaff1728d0e69b95933412241bbccf4f797dba8
- https://git.kernel.org/stable/c/ce54802fe6bb78eb0feffc66fed6a45d41ffc3ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43055.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43055
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
