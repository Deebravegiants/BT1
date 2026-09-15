# [H] usb: typec: altmodes/displayport: fix pin_assignment_show

## Summary
Severity: High
Advisory: CVE-2023-54186
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54186
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: typec: altmodes/displayport: fix pin_assignment_show

This patch fixes negative indexing of buf array in pin_assignment_show
when get_current_pin_assignments returns 0 i.e. no compatible pin
assignments are found.

BUG: KASAN: use-after-free in pin_assignment_show+0x26c/0x33c
...
Call trace:
dump_backtrace+0x110/0x204
dump_stack_lvl+0x84/0xbc
print_report+0x358/0x974
kasan_report+0x9c/0xfc
__do_kernel_fault+0xd4/0x2d4
do_bad_area+0x48/0x168
do_tag_check_fault+0x24/0x38
do_mem_abort+0x6c/0x14c
el1_abort+0x44/0x68
el1h_64_sync_handler+0x64/0xa4
el1h_64_sync+0x78/0x7c
pin_assignment_show+0x26c/0x33c
dev_attr_show+0x50/0xc0

## References
- https://git.kernel.org/stable/c/08bd1be1c716fd50a7df48f82dcbc59a103082b5
- https://git.kernel.org/stable/c/0e61a7432fcd4bca06f05b7f1c7d7cb461880fe2
- https://git.kernel.org/stable/c/4f9c0a7c272626cb6716ffc7800e8c73260cdce6
- https://git.kernel.org/stable/c/54ee23e4ab263a495ace1eed43d3883212ece17f
- https://git.kernel.org/stable/c/d8f28269dd4bf9b55c3fb376ae31512730a96fce
- https://git.kernel.org/stable/c/fc0e18f95c88435bd8a1ceb540243cd7fbcd9781
- https://git.kernel.org/stable/c/ff466f77d0a56719979c4234abd412abd98eae8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54186.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
