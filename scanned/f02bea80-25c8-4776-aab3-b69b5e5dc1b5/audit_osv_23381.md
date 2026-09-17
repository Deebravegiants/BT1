# [M] scsi: qla2xxx: Fix memory leak in __qlt_24xx_handle_abts()

## Summary
Severity: Medium
Advisory: CVE-2022-48650
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48650
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.71, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix memory leak in __qlt_24xx_handle_abts()

Commit 8f394da36a36 ("scsi: qla2xxx: Drop TARGET_SCF_LOOKUP_LUN_FROM_TAG")
made the __qlt_24xx_handle_abts() function return early if
tcm_qla2xxx_find_cmd_by_tag() didn't find a command, but it missed to clean
up the allocated memory for the management command.

## References
- https://git.kernel.org/stable/c/601be20fc6a1b762044d2398befffd6bf236cebf
- https://git.kernel.org/stable/c/6a4236ed47f5b0a57eb6b8fb1c351b15b3d341d7
- https://git.kernel.org/stable/c/89df49e561b4a8948521fc3f8a013012eaa08f82
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48650.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48650
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
