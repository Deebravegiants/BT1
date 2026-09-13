# [H] scsi: core: Run queues for all non-SDEV_DEL devices from scsi_run_host_queues

## Summary
Severity: High
Advisory: CVE-2026-64003
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64003
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: core: Run queues for all non-SDEV_DEL devices from scsi_run_host_queues

While a SCSI host is in a recovery state, scsi_mq_requeue_cmd() will not
set the requeue list for a requeued command to be kicked in the future.
The expectation is a call to scsi_run_host_queues() will kick all SCSI
devices once the recovery state is cleared.

However, scsi_run_host_queues() uses shost_for_each_device() which uses
scsi_device_get() and so will ignore devices in a partially removed
state like SDEV_CANCEL. But these devices may also have requeued
requests, leaving their requests stuck from not being kicked and causing
the removal process of the device to hang.

scsi_run_host_queues() needs to run against more devices than the macro
shost_for_each_device() allows. Instead of using the too limiting
scsi_device_get() state checks, only ignore devices in SDEV_DEL state or
when unable to acquire a reference. Attempt to run the queues for all
other devices when scsi_run_host_queues() is called.

## References
- https://git.kernel.org/stable/c/15fb19af49f2073ed77fad16aaabc648b0ca6800
- https://git.kernel.org/stable/c/475f2b37a78f4c698967a7f14f325f04e24c9175
- https://git.kernel.org/stable/c/7205b58702273baf21d6ba7992e6ba15852325f7
- https://git.kernel.org/stable/c/c740e13e7fe32d8e4d9a1699f65b8daf6709895a
- https://git.kernel.org/stable/c/d4dddfecdbb5467bef158d4e1486459808357fef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64003.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64003
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
