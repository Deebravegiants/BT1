# [C] scsi: target: iscsit: Free cmds before session free

## Summary
Severity: Critical
Advisory: CVE-2023-54184
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54184
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: iscsit: Free cmds before session free

Commands from recovery entries are freed after session has been closed.
That leads to use-after-free at command free or NPE with such call trace:

Time2Retain timer expired for SID: 1, cleaning up iSCSI session.
BUG: kernel NULL pointer dereference, address: 0000000000000140
RIP: 0010:sbitmap_queue_clear+0x3a/0xa0
Call Trace:
 target_release_cmd_kref+0xd1/0x1f0 [target_core_mod]
 transport_generic_free_cmd+0xd1/0x180 [target_core_mod]
 iscsit_free_cmd+0x53/0xd0 [iscsi_target_mod]
 iscsit_free_connection_recovery_entries+0x29d/0x320 [iscsi_target_mod]
 iscsit_close_session+0x13a/0x140 [iscsi_target_mod]
 iscsit_check_post_dataout+0x440/0x440 [iscsi_target_mod]
 call_timer_fn+0x24/0x140

Move cleanup of recovery enrties to before session freeing.

## References
- https://git.kernel.org/stable/c/1911cca5916b6e106de7afa3ec0a38447158216c
- https://git.kernel.org/stable/c/4621e24c9257c6379343bf0c11b473817cf7edcd
- https://git.kernel.org/stable/c/4ce221d295f53e6c6b835ab33181e735482c9aac
- https://git.kernel.org/stable/c/89f5055f9b0b57c7e7f02e32df95ef401f809b71
- https://git.kernel.org/stable/c/a7a4def6c7046e090bb10c6d550fdeb487db98ba
- https://git.kernel.org/stable/c/d8990b5a4d065f38f35d69bcd627ec5a7f8330ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54184.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54184
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
