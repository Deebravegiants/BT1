# [H] scsi: qedi: Fix use after free bug in qedi_remove()

## Summary
Severity: High
Advisory: CVE-2023-54100
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54100
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.180, >=5.11.0 <5.15.112, >=5.16.0 <6.1.29, >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qedi: Fix use after free bug in qedi_remove()

In qedi_probe() we call __qedi_probe() which initializes
&qedi->recovery_work with qedi_recovery_handler() and
&qedi->board_disable_work with qedi_board_disable_work().

When qedi_schedule_recovery_handler() is called, schedule_delayed_work()
will finally start the work.

In qedi_remove(), which is called to remove the driver, the following
sequence may be observed:

Fix this by finishing the work before cleanup in qedi_remove().

CPU0                  CPU1

                     |qedi_recovery_handler
qedi_remove          |
  __qedi_remove      |
iscsi_host_free      |
scsi_host_put        |
//free shost         |
                     |iscsi_host_for_each_session
                     |//use qedi->shost

Cancel recovery_work and board_disable_work in __qedi_remove().

## References
- https://git.kernel.org/stable/c/124027cd1a624ce0347adcd59241a9966a726b22
- https://git.kernel.org/stable/c/3738a230831e861503119ee2691c4a7dc56ed60a
- https://git.kernel.org/stable/c/5e756a59cee6a8a79b9059c5bdf0ecbf5bb8d151
- https://git.kernel.org/stable/c/89f6023fc321c958a0fb11f143a6eb4544ae3940
- https://git.kernel.org/stable/c/c5749639f2d0a1f6cbe187d05f70c2e7c544d748
- https://git.kernel.org/stable/c/fa19c533ab19161298f0780bcc6523af88f6fd20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54100.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
