# [H] scsi: qla2xxx: validate nvme_local_port correctly

## Summary
Severity: High
Advisory: CVE-2024-42286
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42286
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: validate nvme_local_port correctly

The driver load failed with error message,

qla2xxx [0000:04:00.0]-ffff:0: register_localport failed: ret=ffffffef

and with a kernel crash,

	BUG: unable to handle kernel NULL pointer dereference at 0000000000000070
	Workqueue: events_unbound qla_register_fcport_fn [qla2xxx]
	RIP: 0010:nvme_fc_register_remoteport+0x16/0x430 [nvme_fc]
	RSP: 0018:ffffaaa040eb3d98 EFLAGS: 00010282
	RAX: 0000000000000000 RBX: ffff9dfb46b78c00 RCX: 0000000000000000
	RDX: ffff9dfb46b78da8 RSI: ffffaaa040eb3e08 RDI: 0000000000000000
	RBP: ffff9dfb612a0a58 R08: ffffffffaf1d6270 R09: 3a34303a30303030
	R10: 34303a303030305b R11: 2078787832616c71 R12: ffff9dfb46b78dd4
	R13: ffff9dfb46b78c24 R14: ffff9dfb41525300 R15: ffff9dfb46b78da8
	FS:  0000000000000000(0000) GS:ffff9dfc67c00000(0000) knlGS:0000000000000000
	CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
	CR2: 0000000000000070 CR3: 000000018da10004 CR4: 00000000000206f0
	Call Trace:
	qla_nvme_register_remote+0xeb/0x1f0 [qla2xxx]
	? qla2x00_dfs_create_rport+0x231/0x270 [qla2xxx]
	qla2x00_update_fcport+0x2a1/0x3c0 [qla2xxx]
	qla_register_fcport_fn+0x54/0xc0 [qla2xxx]

Exit the qla_nvme_register_remote() function when qla_nvme_register_hba()
fails and correctly validate nvme_local_port.

## References
- https://git.kernel.org/stable/c/3eac973eb5cb2b874b3918f924798afc5affd46b
- https://git.kernel.org/stable/c/549aac9655320c9b245a24271b204668c5d40430
- https://git.kernel.org/stable/c/7cec2c3bfe84539c415f5e16f989228eba1d2f1e
- https://git.kernel.org/stable/c/a3ab508a4853a9f5ae25a7816a4889f09938f63c
- https://git.kernel.org/stable/c/cde43031df533751b4ead37d173922feee2f550f
- https://git.kernel.org/stable/c/e1f010844443c389bc552884ac5cfa47de34d54c
- https://git.kernel.org/stable/c/eb1d4ce2609584eeb7694866f34d4b213caa3af9
- https://git.kernel.org/stable/c/f6be298cc1042f24d521197af29c7c4eb95af4d5
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42286.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
