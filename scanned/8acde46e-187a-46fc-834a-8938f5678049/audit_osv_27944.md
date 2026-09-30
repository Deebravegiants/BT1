# [H] scsi: target: core: Add TMF to tmr_list handling

## Summary
Severity: High
Advisory: CVE-2024-26845
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26845
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.270, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: core: Add TMF to tmr_list handling

An abort that is responded to by iSCSI itself is added to tmr_list but does
not go to target core. A LUN_RESET that goes through tmr_list takes a
refcounter on the abort and waits for completion. However, the abort will
be never complete because it was not started in target core.

 Unable to locate ITT: 0x05000000 on CID: 0
 Unable to locate RefTaskTag: 0x05000000 on CID: 0.
 wait_for_tasks: Stopping tmf LUN_RESET with tag 0x0 ref_task_tag 0x0 i_state 34 t_state ISTATE_PROCESSING refcnt 2 transport_state active,stop,fabric_stop
 wait for tasks: tmf LUN_RESET with tag 0x0 ref_task_tag 0x0 i_state 34 t_state ISTATE_PROCESSING refcnt 2 transport_state active,stop,fabric_stop
...
 INFO: task kworker/0:2:49 blocked for more than 491 seconds.
 task:kworker/0:2     state:D stack:    0 pid:   49 ppid:     2 flags:0x00000800
 Workqueue: events target_tmr_work [target_core_mod]
Call Trace:
 __switch_to+0x2c4/0x470
 _schedule+0x314/0x1730
 schedule+0x64/0x130
 schedule_timeout+0x168/0x430
 wait_for_completion+0x140/0x270
 target_put_cmd_and_wait+0x64/0xb0 [target_core_mod]
 core_tmr_lun_reset+0x30/0xa0 [target_core_mod]
 target_tmr_work+0xc8/0x1b0 [target_core_mod]
 process_one_work+0x2d4/0x5d0
 worker_thread+0x78/0x6c0

To fix this, only add abort to tmr_list if it will be handled by target
core.

## References
- https://git.kernel.org/stable/c/11f3fe5001ed05721e641f0ecaa7a73b7deb245d
- https://git.kernel.org/stable/c/168ed59170de1fd7274080fe102216162d6826cf
- https://git.kernel.org/stable/c/36bc5040c863b44af06094b22f1e50059227b9cb
- https://git.kernel.org/stable/c/425a571a7e6fc389954cf2564e1edbba3740e171
- https://git.kernel.org/stable/c/83ab68168a3d990d5ff39ab030ad5754cbbccb25
- https://git.kernel.org/stable/c/a9849b67b4402a12eb35eadc9306c1ef9847d53d
- https://git.kernel.org/stable/c/bd508f96b5fef96d8a0ce9cbb211d82bcfc2341f
- https://git.kernel.org/stable/c/e717bd412001495f17400bfc09f606f1b594ef5a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26845.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26845
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
