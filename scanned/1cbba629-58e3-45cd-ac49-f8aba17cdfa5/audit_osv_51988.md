# [M] CVE-2021-46930

## Summary
Severity: Medium
Advisory: CVE-2021-46930
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46930
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: mtu3: fix list_head check warning

This is caused by uninitialization of list_head.

BUG: KASAN: use-after-free in __list_del_entry_valid+0x34/0xe4

Call trace:
dump_backtrace+0x0/0x298
show_stack+0x24/0x34
dump_stack+0x130/0x1a8
print_address_description+0x88/0x56c
__kasan_report+0x1b8/0x2a0
kasan_report+0x14/0x20
__asan_load8+0x9c/0xa0
__list_del_entry_valid+0x34/0xe4
mtu3_req_complete+0x4c/0x300 [mtu3]
mtu3_gadget_stop+0x168/0x448 [mtu3]
usb_gadget_unregister_driver+0x204/0x3a0
unregister_gadget_item+0x44/0xa4

## References
- https://git.kernel.org/stable/c/3b6efe0b7ba03cc2acf0694b46d6ff33c5b4c295
- https://git.kernel.org/stable/c/585e2b244dda7ea733274e4b8fa27853d625d3bf
- https://git.kernel.org/stable/c/8c313e3bfd9adae8d5c4ba1cc696dcbc86fbf9bf
- https://git.kernel.org/stable/c/249ddfbe00570d6dc76208e88017937d4d374c79
