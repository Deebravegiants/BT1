# [H] scsi: mpi3mr: Fix missing mrioc->evtack_cmds initialization

## Summary
Severity: High
Advisory: CVE-2023-54234
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54234
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpi3mr: Fix missing mrioc->evtack_cmds initialization

Commit c1af985d27da ("scsi: mpi3mr: Add Event acknowledgment logic")
introduced an array mrioc->evtack_cmds but initialization of the array
elements was missed. They are just zero cleared. The function
mpi3mr_complete_evt_ack() refers host_tag field of the elements. Due to the
zero value of the host_tag field, the function calls clear_bit() for
mrico->evtack_cmds_bitmap with wrong bit index. This results in memory
access to invalid address and "BUG: KASAN: use-after-free". This BUG was
observed at eHBA-9600 firmware update to version 8.3.1.0. To fix it, add
the missing initialization of mrioc->evtack_cmds.

## References
- https://git.kernel.org/stable/c/4e0dfdb48a824deac3dfbc67fb856ef2aee13529
- https://git.kernel.org/stable/c/67989091e11a974003ddf2ec39bc613df8eadd83
- https://git.kernel.org/stable/c/e39ea831ebad4ab15c4748cb62a397a8abcca36e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54234.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54234
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
