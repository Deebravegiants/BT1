# [H] scsi: target: configfs: Bound snprintf() return in tg_pt_gp_members_show()

## Summary
Severity: High
Advisory: CVE-2026-46149
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46149
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: configfs: Bound snprintf() return in tg_pt_gp_members_show()

target_tg_pt_gp_members_show() formats LUN paths with snprintf() into a
256-byte stack buffer, then will memcpy() cur_len bytes from that
buffer.  snprintf() returns the length the output would have had, which
can exceed the buffer size when the fabric WWN is long because iSCSI IQN
names can be up to 223 bytes.  The check at the memcpy() site only
guards the destination page write, not the source read, so memcpy() will
read past the stack buffer and copy adjacent stack contents to the sysfs
reader, which when CONFIG_FORTIFY_SOURCE is enabled, fortify_panic()
will be triggered.

Commit 27e06650a5ea ("scsi: target: target_core_configfs: Add length
check to avoid buffer overflow") added the same bound to the
target_lu_gp_members_show() but the tg_pt_gp variant was missed so
resolve that here.

## References
- https://git.kernel.org/stable/c/00d91bfdce5033f5d9b4915638ae9b0553848b5d
- https://git.kernel.org/stable/c/12f2201a56957ba020392223a7393a5eba080c1b
- https://git.kernel.org/stable/c/1f678d13e939f91840cb1ebe9b88544923539d3c
- https://git.kernel.org/stable/c/72cc5ea7ef32bb5fa38bf0dd2e56fcd73aa8c89e
- https://git.kernel.org/stable/c/772a896a56e0e3ef9424a025cec9176f9d8f4552
- https://git.kernel.org/stable/c/d3cc9d490c207d57a289054397349f6f8c90354e
- https://git.kernel.org/stable/c/db0a4759d62cad4ff891e2d81ae4be73bb57f4a4
- https://git.kernel.org/stable/c/e501154f9d82c95d2719bcbbaf679d8fd3226ef7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46149.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46149
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
