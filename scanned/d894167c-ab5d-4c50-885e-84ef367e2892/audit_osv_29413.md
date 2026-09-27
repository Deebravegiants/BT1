# [H] dev/parport: fix the array out-of-bounds risk

## Summary
Severity: High
Advisory: CVE-2024-42301
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42301
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

dev/parport: fix the array out-of-bounds risk

Fixed array out-of-bounds issues caused by sprintf
by replacing it with snprintf for safer data copying,
ensuring the destination buffer is not overflowed.

Below is the stack trace I encountered during the actual issue:

[ 66.575408s] [pid:5118,cpu4,QThread,4]Kernel panic - not syncing: stack-protector:
Kernel stack is corrupted in: do_hardware_base_addr+0xcc/0xd0 [parport]
[ 66.575408s] [pid:5118,cpu4,QThread,5]CPU: 4 PID: 5118 Comm:
QThread Tainted: G S W O 5.10.97-arm64-desktop #7100.57021.2
[ 66.575439s] [pid:5118,cpu4,QThread,6]TGID: 5087 Comm: EFileApp
[ 66.575439s] [pid:5118,cpu4,QThread,7]Hardware name: HUAWEI HUAWEI QingYun
PGUX-W515x-B081/SP1PANGUXM, BIOS 1.00.07 04/29/2024
[ 66.575439s] [pid:5118,cpu4,QThread,8]Call trace:
[ 66.575469s] [pid:5118,cpu4,QThread,9] dump_backtrace+0x0/0x1c0
[ 66.575469s] [pid:5118,cpu4,QThread,0] show_stack+0x14/0x20
[ 66.575469s] [pid:5118,cpu4,QThread,1] dump_stack+0xd4/0x10c
[ 66.575500s] [pid:5118,cpu4,QThread,2] panic+0x1d8/0x3bc
[ 66.575500s] [pid:5118,cpu4,QThread,3] __stack_chk_fail+0x2c/0x38
[ 66.575500s] [pid:5118,cpu4,QThread,4] do_hardware_base_addr+0xcc/0xd0 [parport]

## References
- https://git.kernel.org/stable/c/166a0bddcc27de41fe13f861c8348e8e53e988c8
- https://git.kernel.org/stable/c/47b3dce100778001cd76f7e9188944b5cb27a76d
- https://git.kernel.org/stable/c/7789a1d6792af410aa9b39a1eb237ed24fa2170a
- https://git.kernel.org/stable/c/7f4da759092a1a6ce35fb085182d02de8cc4cc84
- https://git.kernel.org/stable/c/a44f88f7576bc1916d8d6293f5c62fbe7cbe03e0
- https://git.kernel.org/stable/c/ab11dac93d2d568d151b1918d7b84c2d02bacbd5
- https://git.kernel.org/stable/c/b579ea3516c371ecf59d073772bc45dfd28c8a0e
- https://git.kernel.org/stable/c/c719b393374d3763e64900ee19aaed767d5a08d6
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42301.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42301
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
