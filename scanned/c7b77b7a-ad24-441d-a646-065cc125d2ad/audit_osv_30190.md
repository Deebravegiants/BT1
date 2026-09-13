# [H] bpf: Preserve param->string when parsing mount options

## Summary
Severity: High
Advisory: CVE-2024-50165
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50165
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Preserve param->string when parsing mount options

In bpf_parse_param(), keep the value of param->string intact so it can
be freed later. Otherwise, the kmalloc area pointed to by param->string
will be leaked as shown below:

unreferenced object 0xffff888118c46d20 (size 8):
  comm "new_name", pid 12109, jiffies 4295580214
  hex dump (first 8 bytes):
    61 6e 79 00 38 c9 5c 7e                          any.8.\~
  backtrace (crc e1b7f876):
    [<00000000c6848ac7>] kmemleak_alloc+0x4b/0x80
    [<00000000de9f7d00>] __kmalloc_node_track_caller_noprof+0x36e/0x4a0
    [<000000003e29b886>] memdup_user+0x32/0xa0
    [<0000000007248326>] strndup_user+0x46/0x60
    [<0000000035b3dd29>] __x64_sys_fsconfig+0x368/0x3d0
    [<0000000018657927>] x64_sys_call+0xff/0x9f0
    [<00000000c0cabc95>] do_syscall_64+0x3b/0xc0
    [<000000002f331597>] entry_SYSCALL_64_after_hwframe+0x4b/0x53

## References
- https://git.kernel.org/stable/c/1f97c03f43fadc407de5b5cb01c07755053e1c22
- https://git.kernel.org/stable/c/5d7a0a426540319327309035509cb768a2f5c2c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50165.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50165
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
