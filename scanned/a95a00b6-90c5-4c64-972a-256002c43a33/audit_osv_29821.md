# [H] scsi: lpfc: Handle mailbox timeouts in lpfc_get_sfp_info

## Summary
Severity: High
Advisory: CVE-2024-46842
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46842
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Handle mailbox timeouts in lpfc_get_sfp_info

The MBX_TIMEOUT return code is not handled in lpfc_get_sfp_info and the
routine unconditionally frees submitted mailbox commands regardless of
return status.  The issue is that for MBX_TIMEOUT cases, when firmware
returns SFP information at a later time, that same mailbox memory region
references previously freed memory in its cmpl routine.

Fix by adding checks for the MBX_TIMEOUT return code.  During mailbox
resource cleanup, check the mbox flag to make sure that the wait did not
timeout.  If the MBOX_WAKE flag is not set, then do not free the resources
because it will be freed when firmware completes the mailbox at a later
time in its cmpl routine.

Also, increase the timeout from 30 to 60 seconds to accommodate boot
scripts requiring longer timeouts.

## References
- https://git.kernel.org/stable/c/bba47fe3b038cca3d3ebd799665ce69d6d273b58
- https://git.kernel.org/stable/c/ede596b1434b57c0b3fd5c02b326efe5c54f6e48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46842.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46842
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
