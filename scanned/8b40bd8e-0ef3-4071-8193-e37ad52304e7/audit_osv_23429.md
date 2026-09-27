# [H] arm64: extable: fix load_unaligned_zeropad() reg indices

## Summary
Severity: High
Advisory: CVE-2022-48762
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48762
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: extable: fix load_unaligned_zeropad() reg indices

In ex_handler_load_unaligned_zeropad() we erroneously extract the data and
addr register indices from ex->type rather than ex->data. As ex->type will
contain EX_TYPE_LOAD_UNALIGNED_ZEROPAD (i.e. 4):
 * We'll always treat X0 as the address register, since EX_DATA_REG_ADDR is
   extracted from bits [9:5]. Thus, we may attempt to dereference an
   arbitrary address as X0 may hold an arbitrary value.
 * We'll always treat X4 as the data register, since EX_DATA_REG_DATA is
   extracted from bits [4:0]. Thus we will corrupt X4 and cause arbitrary
   behaviour within load_unaligned_zeropad() and its caller.

Fix this by extracting both values from ex->data as originally intended.

On an MTE-enabled QEMU image we are hitting the following crash:
 Unable to handle kernel NULL pointer dereference at virtual address 0000000000000000
 Call trace:
  fixup_exception+0xc4/0x108
  __do_kernel_fault+0x3c/0x268
  do_tag_check_fault+0x3c/0x104
  do_mem_abort+0x44/0xf4
  el1_abort+0x40/0x64
  el1h_64_sync_handler+0x60/0xa0
  el1h_64_sync+0x7c/0x80
  link_path_walk+0x150/0x344
  path_openat+0xa0/0x7dc
  do_filp_open+0xb8/0x168
  do_sys_openat2+0x88/0x17c
  __arm64_sys_openat+0x74/0xa0
  invoke_syscall+0x48/0x148
  el0_svc_common+0xb8/0xf8
  do_el0_svc+0x28/0x88
  el0_svc+0x24/0x84
  el0t_64_sync_handler+0x88/0xec
  el0t_64_sync+0x1b4/0x1b8
 Code: f8695a69 71007d1f 540000e0 927df12a (f940014a)

## References
- https://git.kernel.org/stable/c/3758a6c74e08bdc15ccccd6872a6ad37d165239a
- https://git.kernel.org/stable/c/47fe7a1c5e3e011eeb4ab79f2d54a794fdd1c3eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48762.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48762
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
